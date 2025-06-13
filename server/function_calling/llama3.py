import os
import json
import logging
from dataclasses import dataclass
from typing import Optional

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, Pipeline
from transformers import pipeline
from trl import setup_chat_format

from .download_drive import download_google_drive_folder
from .actions.wolfram import ask_wolfram_question
from .actions.wikipedia import get_wiki_pageInfo

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
    """Llama‑3 wrapper with JSON‑style tool handling and simplified GPU load.
    Assumes English input/output and requires no translation libraries.

    The constructor now mirrors the parameters expected by *service.py*:
        LLama3(model_dir="…", tokenizer_dir="…", ...)
    It also keeps optional *model_link/tokenizer_link* for drive downloads
    so existing scripts using those names still work."""

    path_to_model: str
    path_to_tokenizer: str
    functions: str
    model: AutoModelForCausalLM
    tokenizer: AutoTokenizer
    pipeline: Pipeline
    chat: list[dict[str, str]] = []
    chat_length: int = 0

    _TUTOR_DELEGATE = "tutorai"

    # ─────────────────────────── init / setup ───────────────────────────
    def __init__(
        self,
        model_dir: str | None = None,
        tokenizer_dir: str | None = None,
        *,
        model_link: str | None = None,
        tokenizer_link: str | None = None,
        destination_path: str | None = None,
    ) -> None:
        """Create a wrapper.

        Parameters
        ----------
        model_dir / tokenizer_dir
            Absolute or relative paths to the downloaded weights/tokenizer
            directories. **These are what `service.py` passes in.**
        model_link / tokenizer_link
            Google‑Drive folder IDs or share links – used when the local dirs
            don’t exist yet.
        destination_path
            (Legacy) base name used to derive the two folders when *dir* args
            are omitted. Kept for compatibility with older scripts.
        """
        base_dir = os.path.dirname(__file__)

        # Resolve paths priority: explicit dirs > destination_path fallback
        if model_dir and tokenizer_dir:
            self.path_to_model = os.path.abspath(model_dir)
            self.path_to_tokenizer = os.path.abspath(tokenizer_dir)
        elif destination_path is not None:
            self.path_to_model = os.path.join(base_dir, destination_path + "-model")
            self.path_to_tokenizer = os.path.join(base_dir, destination_path + "-tokenizer")
        else:
            raise ValueError("You must supply either model_dir/tokenizer_dir or destination_path.")

        # Auto‑download if missing and a link is provided
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
        func_path = os.path.join(os.path.dirname(__file__), "functions.json")
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
        self._append_to_chat("user", user_input)
        prompt = self.pipeline.tokenizer.apply_chat_template(
            self.chat, tokenize=False, add_generation_prompt=True
        )
        outputs = self.pipeline(
            prompt,
            max_new_tokens=512,
            temperature=0.1,
            top_k=50,
            top_p=0.1,
            eos_token_id=self.pipeline.tokenizer.eos_token_id,
            pad_token_id=self.pipeline.tokenizer.pad_token_id,
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
        # 1️⃣ Generate initial assistant reply
        assistant_raw = self._generate(transcription)

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

        return LlamaOutput(text=assistant_raw, function_called=function_called)
