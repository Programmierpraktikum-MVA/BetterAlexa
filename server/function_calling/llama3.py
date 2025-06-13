import os
import json
import logging
from dataclasses import dataclass
from typing import Optional

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, Pipeline
from transformers import pipeline
from trl import setup_chat_format
from deep_translator import GoogleTranslator
from lingua import Language, LanguageDetectorBuilder

from .download_drive import download_google_drive_folder
from .actions.wolfram import ask_wolfram_question
from .actions.wikipedia import get_wiki_pageInfo
from .tutor_ai.backend.ChatEngine import ask_TutorAI_question

DEBUG_MODE = 1


# ───────────────────────── output dataclass ────────────────────────────
@dataclass
class LlamaOutput:
    """Structured return type expected by service.py."""

    text: str
    delegate: bool = False
    delegate_target: Optional[str] = None
    function_called: bool = False


class LLama3:
    """Simplified Llama‑3 wrapper that mirrors llama3.py but keeps JSON‑style
    tool handling from `llama3_goal.py`. We assume enough VRAM, so the model is
    *always* loaded in 4‑bit on GPU – no heuristics, no fallbacks."""

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

    _TUTOR_DELEGATE = "tutorai"

    # ─────────────────────────── init / setup ───────────────────────────
    def __init__(self, destination_path: str, model_link: str | None = None, tokenizer_link: str | None = None) -> None:
        self.path_to_dir = os.path.dirname(__file__)
        self.path_to_model = os.path.join(self.path_to_dir, destination_path + "-model")
        self.path_to_tokenizer = os.path.join(self.path_to_dir, destination_path + "-tokenizer")
        self.lang_detector = LanguageDetectorBuilder.from_languages(Language.GERMAN, Language.ENGLISH).build()

        if model_link and not os.path.isdir(self.path_to_model):
            download_google_drive_folder(model_link, self.path_to_model)

        if tokenizer_link and not os.path.isdir(self.path_to_tokenizer):
            download_google_drive_folder(tokenizer_link, self.path_to_tokenizer)

        self._load_functions()
        system_msg = (
            "You are a helpful assistant with access to the following functions. "
            "Use them if required -\n{\n" + self.functions + "\n}"
        )
        self._append_to_chat("system", system_msg)
        self._prepare_model()

    # ─────────────────────── chat memory helpers ───────────────────────
    def _append_to_chat(self, role: str, content: str):
        msg = {"role": role, "content": content}
        self.chat.append(msg)
        self.chat_length += len(content.split())
        while self.chat_length > 1024 and len(self.chat) > 2:
            removed = self.chat.pop(1)
            self.chat_length -= len(removed["content"].split())

    # ─────────────────────────── utilities ─────────────────────────────
    def _load_functions(self):
        func_path = os.path.join(self.path_to_dir, "functions.json")
        with open(func_path, "r", encoding="utf-8") as file:
            self.functions = file.read()

    # ─────────────────────────── model load ────────────────────────────
    def _prepare_model(self):
        tokenizer = AutoTokenizer.from_pretrained(self.path_to_tokenizer)
        tokenizer.padding_side = "right"

        quant_cfg = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
        )
        model = AutoModelForCausalLM.from_pretrained(
            self.path_to_model,
            device_map="auto",
            quantization_config=quant_cfg,
            torch_dtype=torch.float16,
        )

        self.model, self.tokenizer = setup_chat_format(model, tokenizer)
        self.pipeline = pipeline("text-generation", model=self.model, tokenizer=self.tokenizer)

    # ───────────────────────── generation core ─────────────────────────
    def _generate(self, user_input: str) -> str:
        """Handles chat bookkeeping and returns the raw assistant string."""
        self._append_to_chat("user", user_input)
        prompt = self.pipeline.tokenizer.apply_chat_template(
            self.chat, tokenize=False, add_generation_prompt=True
        )
        eos_token_id = self.pipeline.tokenizer.eos_token_id
        pad_token_id = self.pipeline.tokenizer.pad_token_id

        outputs = self.pipeline(
            prompt,
            max_new_tokens=512,
            temperature=0.1,
            top_k=50,
            top_p=0.1,
            eos_token_id=eos_token_id,
            pad_token_id=pad_token_id,
        )
        response = outputs[0]["generated_text"][len(prompt) :].strip()
        self._append_to_chat("assistant", response)
        return response

    # ─────────────────────── function‑call handler ──────────────────────
    def _handle_function_call(self, fc_text: str) -> str:
        if DEBUG_MODE:
            print(fc_text)
        payload_str = fc_text[len("<functioncall> ") :].replace("'", "")
        try:
            data = json.loads(payload_str)
        except Exception:
            return self._generate("FUNCTION RESPONSE: Invalid input format, try again")

        name = data.get("name", "")
        arguments = data.get("arguments", {})
        func = globals().get(name)
        if callable(func):
            try:
                result = func(**arguments)
            except Exception as exc:
                result = f"<error>{exc}</error>"
        else:
            result = f"<error>Unknown tool: {name}</error>"

        return self._generate("FUNCTION RESPONSE: " + str({"result": result}))

    # ───────────────────────── public API ──────────────────────────────
    def process_input(self, transcription: str) -> LlamaOutput:  # noqa: C901 – keep logic linear
        try:
            lang_detected = self.lang_detector.detect_language_of(transcription).iso_code_639_1.name.lower()
        except Exception:
            lang_detected = "en"

        user_input = transcription if lang_detected == "en" else GoogleTranslator("auto", "en").translate(transcription)

        # 1️⃣ Generate initial assistant reply
        assistant_raw = self._generate(user_input)

        # 2️⃣ Function‑call or delegation handling
        function_called = False
        if assistant_raw.startswith("<functioncall> "):
            payload_str = assistant_raw[len("<functioncall> ") :].replace("'", "")
            try:
                payload = json.loads(payload_str)
            except Exception:
                payload = {}
            fname = payload.get("name", "").lower()

            if fname.startswith("ask_tutorai"):
                return LlamaOutput(text="", delegate=True, delegate_target=self._TUTOR_DELEGATE)

            assistant_raw = self._handle_function_call(assistant_raw)
            function_called = True

        # 3️⃣ Translate back to original language if necessary
        final_answer = assistant_raw if lang_detected == "en" else GoogleTranslator("en", lang_detected).translate(assistant_raw)

        return LlamaOutput(text=final_answer, function_called=function_called)
