"""Llama‑3 wrapper with structured output and dynamic function‑calling.

* Parses `functions.json` at startup and advertises every function therein
  **except** those that target TutorAI (these are delegated instead).
* Executes recognised function‑calls inline and feeds their return value back
  into the model so it can weave the result into a natural‑language answer.
"""
from __future__ import annotations

import importlib
import json
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    pipeline,
)

# Regex that extracts <functioncall>{…}</functioncall>
_TOOL_REGEX = re.compile(r"<functioncall>(.*?)</functioncall>", re.DOTALL | re.IGNORECASE)


@dataclass
class LlamaOutput:
    text: str
    delegate: bool = False
    delegate_target: Optional[str] = None
    function_called: bool = False


class LLama3:
    """Drop‑in Llama‑3 wrapper for BetterAlexa with smart tool support."""

    def __init__(
        self,
        model_dir: Path,
        tokenizer_dir: Path,
        *,
        functions_file: Path = Path(__file__).with_name("functions.json"),
        tutor_delegate: str = "TutorAI",
        max_new_tokens: int = 64,
    ) -> None:
        # ══════════════════ load functions spec ══════════════════════
        with functions_file.open("r", encoding="utf‑8") as f:
            self.functions_spec: List[Dict[str, Any]] = json.load(f)

        # Split into locally‑handled vs delegated (TutorAI) buckets
        self.local_funcs = [f for f in self.functions_spec if tutor_delegate.lower() not in f["name"].lower()]
        self.delegate_funcs = [f for f in self.functions_spec if f not in self.local_funcs]
        self.tutor_delegate_name = tutor_delegate.lower()

        # ══════════════════ HF model + tokenizer ═════════════════════
        quant_cfg = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
        )
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_dir, local_files_only=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_dir,
            quantization_config=quant_cfg,
            device_map="auto",
            local_files_only=True,
        )
        self.pipe = pipeline("text-generation", model=self.model, tokenizer=self.tokenizer, device_map="auto")

        # ══════════════════ tool registry ════════════════════════════
        self.max_new_tokens = max_new_tokens
        self.tools: Dict[str, Any] = self._load_tools()

    # ──────────────────────── public api ────────────────────────────
    def process_input(self, user_text: str) -> LlamaOutput:
        logging.debug("Processing input: %s", user_text)
        prompt = self._build_prompt(user_text)
        raw_answer = self._generate(prompt)
        logging.debug("Raw model output: %s", raw_answer)

        match = _TOOL_REGEX.search(raw_answer)
        if match:
            payload = json.loads(match.group(1).strip())
            name: str | None = payload.get("name")
            args: Dict[str, Any] = payload.get("arguments", {})
            logging.debug("Function‑call payload detected: %s", payload)

            # ───── delegation (TutorAI or future hard‑coded services) ─────
            if name and name.lower().startswith("ask_tutorai"):
                return LlamaOutput(text="", delegate=True, delegate_target=self.tutor_delegate_name)

            # ───── local execution path ─────
            if name in self.tools:
                try:
                    result = self.tools[name](**args)
                except Exception as exc:  # noqa: BLE001
                    logging.exception("Tool '%s' raised", name)
                    result = f"<error>{exc}</error>"

                follow_up_prompt = (
                    prompt
                    + raw_answer
                    + f"\nFunction `{name}` returned: {result}\nAssistant: "
                )
                final_answer = self._generate(follow_up_prompt)
                return LlamaOutput(text=self._assistant_only(final_answer), function_called=True)

        return LlamaOutput(text=self._assistant_only(raw_answer))

    # ─────────────────────── helper methods ─────────────────────────
    def _assistant_only(self, text: str) -> str:
        """Strip everything past the next role tag so TTS stays sane."""
        m = re.search(r"\n\s*(user|assistant|system)[:\s]", text, re.I)
        return (text[: m.start()] if m else text).strip()

    def _generate(self, prompt: str) -> str:
        out = self.pipe(
            prompt,
            do_sample=False,
            max_new_tokens=self.max_new_tokens,
            return_full_text=False,
            pad_token_id=self.tokenizer.eos_token_id,
            eos_token_id=self.tokenizer.eos_token_id,
        )
        return out[0]["generated_text"]

    def _build_prompt(self, user_text: str) -> str:
        tools_json = json.dumps(self.local_funcs_schema(), indent=2)
        return (
            "You are BetterAlexa. Answer user queries. "
            "If a function/tool is needed, output <functioncall>{JSON}</functioncall>.\n"
            f"Available tools: {tools_json}\n\n"
            f"User: {user_text}\nAssistant: "
        )

    # ═════════════════════ tool loading ═════════════════════════════
    def _load_tools(self) -> Dict[str, Any]:
        """Dynamically import Python callables that match function names.

        By convention we expect a module `skills.<name>` exporting `run(**kwargs)`.
        If the module isn’t found we register a dummy lambda so the flow still
        works (the model gets a placeholder response).
        """
        registry: Dict[str, Any] = {}
        for spec in self.local_funcs:
            fname = spec["name"]
            try:
                mod = importlib.import_module(f"skills.{fname}")
                registry[fname] = getattr(mod, "run")
            except Exception:  # fallback stub
                logging.warning("No implementation for %s – using stub", fname)
                registry[fname] = lambda **_: f"[{fname} executed]"
        return registry

    def local_funcs_schema(self) -> List[Dict[str, Any]]:
        """Return the JSON schema excluding TutorAI entries."""
        return self.local_funcs
