"""Llama‑3 wrapper with structured output and dynamic function‑calling.

Key features
============
* Reads **`functions.json`** on startup and exposes every function except
  those whose *name* contains the substring *TutorAI* (these are delegated).
* Detects and executes `<functioncall>{ … }</functioncall>` blocks even when
  the close‑tag is missing or the JSON uses single quotes.
* Feeds the function result back to the model so it can phrase a natural
  language answer – only that answer is returned to the caller.
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

# ───────────────────────── regex helpers ────────────────────────────
# 1️⃣ Capture JSON between explicit open & close tags (preferred case)
_FUNC_TAG_RE = re.compile(r"<functioncall>(.*?)</functioncall>", re.DOTALL | re.I)
# 2️⃣ Fallback: opening tag only – grab until next role tag or EoS
_FUNC_OPEN_RE = re.compile(r"<functioncall>(.*)", re.DOTALL | re.I)
# Detect the next role tag so we know where the assistant turn ends
_ROLE_RE = re.compile(r"\n\s*(user|assistant|system)[:\s]", re.I)


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
        # ══════════════════ Load function specs ═════════════════════
        with functions_file.open("r", encoding="utf‑8") as fh:
            spec: List[Dict[str, Any]] = json.load(fh)
        self.local_funcs = [f for f in spec if tutor_delegate.lower() not in f["name"].lower()]
        self.delegate_funcs = [f for f in spec if f not in self.local_funcs]
        self.tutor_delegate_name = tutor_delegate.lower()

        # ══════════════════ Model + tokenizer ═══════════════════════
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

        # ══════════════════ Runtime settings ════════════════════════
        self.max_new_tokens = max_new_tokens
        self.tools = self._load_tools()

    # ───────────────────────── Public API ──────────────────────────
    def process_input(self, user_text: str) -> LlamaOutput:
        logging.debug("Processing input: %s", user_text)
        prompt = self._build_prompt(user_text)
        raw_answer = self._generate(prompt)
        logging.debug("Raw model output: %s", raw_answer)

        payload = self._extract_func_payload(raw_answer)
        if payload:
            name = payload.get("name")
            args = payload.get("arguments", {})
            logging.debug("Function‑call detected – name=%s args=%s", name, args)

            # ─── Delegation: TutorAI or future hard‑coded services ───
            if name and name.lower().startswith("ask_tutorai"):
                return LlamaOutput(text="", delegate=True, delegate_target=self.tutor_delegate_name)

            # ─── Local execution ───
            if name in self.tools:
                try:
                    # arguments may be a JSON‑encoded string → parse
                    if isinstance(args, str):
                        args = json.loads(args)
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

        # No recognised function‑call – return trimmed assistant text
        return LlamaOutput(text=self._assistant_only(raw_answer))

    # ─────────────────────── Internal helpers ──────────────────────
    def _extract_func_payload(self, text: str) -> Optional[Dict[str, Any]]:
        """Grab and parse the JSON inside a <functioncall> block."""
        m = _FUNC_TAG_RE.search(text) or _FUNC_OPEN_RE.search(text)
        if not m:
            return None
        json_str = m.group(1)

        # If we matched _FUNC_OPEN_RE, chop off at next role tag
        role_match = _ROLE_RE.search(json_str)
        if role_match:
            json_str = json_str[: role_match.start()]

        json_str = json_str.strip()
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            try:
                fixed = json_str.replace("'", '"')
                return json.loads(fixed)
            except Exception:
                logging.warning("Could not parse function‑call JSON: %s", json_str)
                return None

    def _assistant_only(self, text: str) -> str:
        m = _ROLE_RE.search(text)
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

    # ═══════════════ Tool registry ════════════════════════════════
    def _load_tools(self) -> Dict[str, Any]:
        registry: Dict[str, Any] = {}
        for spec in self.local_funcs:
            fname = spec["name"]
            try:
                mod = importlib.import_module(f"skills.{fname}")
                registry[fname] = getattr(mod, "run")
            except Exception:
                logging.warning("No implementation for %s – using stub", fname)
                registry[fname] = lambda **_: f"[{fname} executed]"
        return registry

    def local_funcs_schema(self) -> List[Dict[str, Any]]:
        return self.local_funcs
