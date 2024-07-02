import torch
import os
import json
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, Pipeline
from transformers import pipeline
from download_drive import download_google_drive_folder
from trl import setup_chat_format
from deep_translator import GoogleTranslator
from lingua import Language, LanguageDetectorBuilder

from actions.wolfram import ask_wolfram_question
from actions.wikipedia import getWikiPageInfo
from actions.spotify_utils import play,set_volume_to,pause,next,prev,turn_on_shuffle,turn_off_shuffle,decrease_volume,increase_volume,play_song,play_album,play_artist,add_to_queue
from tutor_ai.backend.ChatEngine import ask_TutorAI_question

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
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16,
        )
        model = AutoModelForCausalLM.from_pretrained(
            self.path_to_model,
            device_map='auto',
            torch_dtype=torch.bfloat16,
            quantization_config=bnb_config
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
        lang = self.lang_detector.detect_language_of(transcription).iso_code_639_1.name
        lang = lang.lower()
        if lang != 'en':
            transcription = GoogleTranslator("auto", "en").translate(transcription)
        output = self.generate(transcription)
        if output.startswith("<functioncall> "):
            output = self.process_function_call(output)
        if lang != 'en':
            output = GoogleTranslator("en", lang).translate(output)
        return output
    






        
