"""Llama‑3 wrapper with structured output and generic delegation.
Pass `delegate_names=[...]` to register pseudo tools.
"""
from __future__ import annotations

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

# Matches <functioncall>{json…}</functioncall>
_TOOL_REGEX = re.compile(r"<functioncall>(.*?)</functioncall>", re.DOTALL | re.IGNORECASE)


@dataclass
class LlamaOutput:
    """Container for everything the wrapper can return to *service.py*."""

    text: str
    delegate: bool = False
    delegate_target: Optional[str] = None
    function_called: bool = False


class LLama3:
    """Thin convenience wrapper around a local Llama‑3 model.

    Highlights
    ----------
    * **Returns only the assistant’s freshly‑generated text** (never the full
      prompt) so the caller can pipe it straight into TTS.
    * Enforces a hard ``max_new_tokens`` ceiling to avoid run‑away answers.
    * Supports JSON‑wrapped `<functioncall>` tool invocations and optional
      *delegation* placeholders (e.g. forward query to a cloud model).
    """

    def __init__(
        self,
        model_dir: Path,
        tokenizer_dir: Path,
        *,
        delegate_names: Optional[List[str]] = None,
        max_new_tokens: int = 64,
    ) -> None:
        # ───────────────────── model & tokenizer ──────────────────────
        quant_cfg = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
        )

        self.tokenizer = AutoTokenizer.from_pretrained(
            tokenizer_dir,
            local_files_only=True,
        )
        self.model = AutoModelForCausalLM.from_pretrained(
            model_dir,
            quantization_config=quant_cfg,
            device_map="auto",
            local_files_only=True,
        )

        self.pipe = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            device_map="auto",
        )

        # ───────────────────── settings & helpers ─────────────────────
        self.max_new_tokens = max_new_tokens
        self.delegate_names = delegate_names or []
        self.tools = self._load_tools()

    # ────────────────────────── public API ────────────────────────────
    def process_input(self, user_text: str) -> LlamaOutput:
        """Generate an answer or delegation instruction for *user_text*."""
        logging.debug("Processing input: %s", user_text)

        prompt = self._build_prompt(user_text)
        logging.debug("Built prompt: %s", prompt)

        raw_answer = self._generate(prompt)
        logging.debug("Raw model output: %s", raw_answer)

        # ───── Check for <functioncall>{...}</functioncall> blocks ─────
        match = _TOOL_REGEX.search(raw_answer)
        if match:
            payload = json.loads(match.group(1).strip())
            name: str | None = payload.get("name")
            args: Dict[str, Any] = payload.get("arguments", {})
            logging.debug("Detected function‑call payload: %s", payload)

            # Delegation pseudo‑tool — nothing to execute locally.
            if name and name.startswith("delegate_to_"):
                target = name.split("delegate_to_")[-1]
                return LlamaOutput(text="", delegate=True, delegate_target=target)

            # Local tool execution path
            if name in self.tools:
                try:
                    result = self.tools[name](**args)
                except Exception as exc:  # noqa: BLE001 – best‑effort logging
                    logging.exception("Tool '%s' raised", name)
                    result = f"<error>{exc}</error>"

                # Feed the tool result back so the model can respond properly
                follow_up_prompt = (
                    prompt
                    + raw_answer
                    + f"\nFunction `{name}` returned: {result}\nAssistant: "
                )
                final_answer = self._generate(follow_up_prompt)
                return LlamaOutput(
                    text=self._assistant_only(final_answer),
                    function_called=True,
                )

        # No tool usage — return the assistant reply only
        return LlamaOutput(text=self._assistant_only(raw_answer))

    # ─────────────────────── internal helpers ────────────────────────
    def _assistant_only(self, text: str) -> str:
        """Return only the assistant’s reply, cutting off at the next role tag.

        We look for a newline followed by *any* role word (user/assistant/system)
        in *any* capitalisation, optionally followed by a colon or whitespace.
        """
        turn_break = re.search(r"\n\s*(user|assistant|system)[:\s]", text, re.IGNORECASE)
        if turn_break:
            text = text[: turn_break.start()]
        return text.strip()

    def _generate(self, full_prompt: str) -> str:
        """Wrapper around the HF pipeline that applies safe defaults."""
        out = self.pipe(
            full_prompt,
            do_sample=False,  # deterministic; raise temperature & top_p if you need creativity
            max_new_tokens=self.max_new_tokens,
            return_full_text=False,  # return *only* new tokens (no prompt)
            pad_token_id=self.tokenizer.eos_token_id,
            eos_token_id=self.tokenizer.eos_token_id,
        )
        return out[0]["generated_text"]

    def _build_prompt(self, user_text: str) -> str:
        """Construct the system+user prompt we feed to the model."""
        tools_json = json.dumps(self._tools_schema(), indent=2)
        return (
            "You are BetterAlexa. Answer user queries. "
            "If a function/tool is needed, output <functioncall>{JSON}</functioncall>.\n"
            f"Available tools: {tools_json}\n\n"
            f"User: {user_text}\nAssistant: "
        )

    def _load_tools(self) -> Dict[str, Any]:
        """Register built‑in tools and delegation placeholders."""
        registry: Dict[str, Any] = {
            "math_add": lambda a, b: a + b,
        }
        for name in self.delegate_names:
            registry[f"delegate_to_{name}"] = lambda **_: None  # placeholder – handled upstream
        return registry

    def _tools_schema(self) -> List[Dict[str, Any]]:
        """Return OpenAI‑style JSON schema describing available tools."""
        schema: List[Dict[str, Any]] = [
            {
                "name": "math_add",
                "description": "Add two integers",
                "parameters": {"a": "int", "b": "int"},
            }
        ]
        schema += [
            {
                "name": f"delegate_to_{n}",
                "description": f"Delegate to {n}",
                "parameters": {},
            }
            for n in self.delegate_names
        ]
        return schema
