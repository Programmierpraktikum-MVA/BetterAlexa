import torch
import os
import json
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, Pipeline
from transformers import pipeline
from .download_drive import download_google_drive_folder
from trl import setup_chat_format
from deep_translator import GoogleTranslator
from lingua import Language, LanguageDetectorBuilder
import logging
import gpu_utils

from .actions.wolfram import ask_wolfram_question
from .actions.wikipedia import get_wiki_pageInfo

# That should be looked at by @Integrations

# from .actions.spotify_utils import play_artist, play_album, play_song, next, prev, pause, play, increase_volume, decrease_volume, add_to_queue
from .tutor_ai.backend.ChatEngine import ask_TutorAI_question

DEBUG_MODE = 1

class LLama3:
    path_to_model: str
    path_to_tokenizer: str
    path_to_dir: str
    functions: str
    model: AutoModelForCausalLM
    tokenizer: AutoTokenizer
    pipeline: Pipeline
    chat: list[dict[str, str]] = []
    chat_length: int = 0
    lang_detector: LanguageDetectorBuilder

    def _gpu_supports_bnb(self) -> bool:
        """
        True  → we have a CUDA-capable GPU whose compute capability ≥ 7.0  
        (Turing / RTX‑20‑series or newer – the minimum BNB officially
        documents for LLM quantisation)  
        False → no GPU or an older CC (e.g. GTX‑10/50‑series).
        """
        if not torch.cuda.is_available():
            return False
        major, minor = torch.cuda.get_device_capability(0)
        return (major * 10 + minor) >= 70      # 7.0, covers RTX‑20 onwards


    def __init__(self, destination_path: str, model_link: str | None = None, tokenizer_link: str | None = None) -> None:
        self.path_to_dir = os.path.dirname(__file__)
        self.path_to_model = os.path.join(self.path_to_dir, destination_path + "-model")
        self.path_to_tokenizer = os.path.join(self.path_to_dir, destination_path + "-tokenizer")
        self.lang_detector = LanguageDetectorBuilder.from_languages(Language.GERMAN, Language.ENGLISH).build()

        if model_link is not None and not (os.path.exists(self.path_to_model) and os.path.isdir(self.path_to_model)):
            download_google_drive_folder(model_link, self.path_to_model)

        if tokenizer_link is not None and not (os.path.exists(self.path_to_tokenizer) and os.path.isdir(self.path_to_tokenizer)):
            download_google_drive_folder(tokenizer_link, self.path_to_tokenizer)
        
        self.search_functions()
        system_msg = "You are a helpful assistant with access to the following functions. Use them if required -\n{\n" + self.functions + "\n}"
        self.append_to_chat("system", system_msg)
        self.prepare()
    
    def append_to_chat(self, role: str, content: str):
        msg = {"role": role, "content": content}
        self.chat.append(msg)
        self.chat_length += len(msg["content"].split())
        while self.chat_length > 1024:
            msg = self.chat.pop(1)
            self.chat_length -= len(msg["content"].split())

    def search_functions(self):
        func_path = os.path.join(self.path_to_dir, "functions.json")
        with open(func_path, 'r') as file:
            self.functions = file.read()

    def prepare(self):
        tokenizer = AutoTokenizer.from_pretrained(self.path_to_tokenizer)
        tokenizer.padding_side = "right"

        free_gb          = gpu_utils.gpu_free_gb()
        need_4bit_gb     = gpu_utils.LLAMA3_8B_4BIT_GB  + gpu_utils.SAFETY_MARGIN_GB
        need_fp16_gb     = gpu_utils.LLAMA3_8B_16FP_GB + gpu_utils.SAFETY_MARGIN_GB

        can_bnb          = self._gpu_supports_bnb()          # sm ≥ 7.0
        enough_for_4bit  = free_gb >= need_4bit_gb
        enough_for_fp16  = free_gb >= need_fp16_gb

        try:
        # BNB and enough VRAM for 4bit
            if can_bnb and enough_for_4bit:
                from transformers import BitsAndBytesConfig
                bnb_cfg = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="nf4",
                    bnb_4bit_compute_dtype=torch.bfloat16,
                )
                model = AutoModelForCausalLM.from_pretrained(
                    self.path_to_model,
                    device_map="auto",
                    quantization_config=bnb_cfg,
                    torch_dtype=torch.bfloat16,
                )

            # No BNB but enough VRAM for FP16
            elif torch.cuda.is_available() and enough_for_fp16:
                model = AutoModelForCausalLM.from_pretrained(
                    self.path_to_model,
                    device_map="auto",
                    torch_dtype=torch.float16,
                )

            # CPU
            else:
                logging.warning(
                    "Loading Llama on CPU (%.1f GB free VRAM; need ≥ %.1f GB for GPU)",
                    free_gb, need_4bit_gb if can_bnb else need_fp16_gb,
                )
                model = AutoModelForCausalLM.from_pretrained(
                    self.path_to_model,
                    device_map={"": "cpu"},
                    torch_dtype=torch.float32,
                )
        except (ImportError, OSError, ValueError, RuntimeError) as e:
            # Any unexpected CUDA/bits‑and‑bytes issue → retry on CPU
            logging.warning("GPU load failed (%s) – retrying on CPU", e)
            torch.cuda.empty_cache()
            model = AutoModelForCausalLM.from_pretrained(
                self.path_to_model,
                device_map={"": "cpu"},
                torch_dtype=torch.float32,
            )

        self.model, self.tokenizer = setup_chat_format(model, tokenizer)
        self.pipeline = pipeline("text-generation", model=self.model, tokenizer=self.tokenizer)


    def generate(self, input: str) -> str:
        self.append_to_chat("user", input)
        prompt = self.pipeline.tokenizer.apply_chat_template(self.chat, tokenize=False, add_generation_prompt=True)

        eos_token_id = self.pipeline.tokenizer.eos_token_id
        pad_token_id = self.pipeline.tokenizer.pad_token_id

        outputs = self.pipeline(prompt, max_new_tokens=512, temperature=0.1, top_k=50, top_p=0.1, eos_token_id=eos_token_id, pad_token_id=pad_token_id)
        response = outputs[0]['generated_text'][len(prompt):].strip()
        self.append_to_chat("assistant", response)
        return response
    
    def process_function_call(self, fc: str) -> str:
        if DEBUG_MODE:
            print(fc)
        fc = fc[len("<functioncall> "):]
        fc = fc.replace("'", "")
        try: 
            data = json.loads(fc)
        except:
            result = 'FUNCTION RESPONSE: Invalid input format, try again' 
            if DEBUG_MODE:
                print(result)
            return self.generate(result)
        name = data["name"]
        arguments = data["arguments"]
        result = globals()[name](**arguments)
        result = {"result": result}
        result = 'FUNCTION RESPONSE: ' + str(result)
        if DEBUG_MODE:
            print(result)
        return self.generate(result)

    def process_input(self, transcription: str):
        try:
            lang = self.lang_detector.detect_language_of(transcription).iso_code_639_1.name
        except Exception as e:
            lang = "en"

        lang = lang.lower()
        if lang != 'en':
            transcription = GoogleTranslator("auto", "en").translate(transcription)
        output = self.generate(transcription)
        if output.startswith("<functioncall> "):
            output = self.process_function_call(output)
        if lang != 'en':
            output = GoogleTranslator("en", lang).translate(output)
        return output
    






        
