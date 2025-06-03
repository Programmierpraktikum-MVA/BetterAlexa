"""Llama‑3 wrapper with structured output and generic delegation.
Pass `delegate_names=[...]` to register pseudo tools.
"""
from __future__ import annotations

from pathlib import Path
import json
import logging
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    pipeline,
)

# ⬇ matches <functioncall>{json…}</functioncall>
_TOOL_REGEX = re.compile(r"<functioncall>(.*?)</functioncall>", re.DOTALL)


@dataclass
class LlamaOutput:
    text: str
    delegate: bool = False
    delegate_target: Optional[str] = None
    function_called: bool = False


class LLama3:
    """Thin convenience wrapper around a local Llama‑3 model.

    * Ensures we **only return the newly‑generated answer tokens** back to
      the caller (FastAPI service) – never the full prompt.
    * Adds a hard *max_new_tokens* cap so the model can’t run away.
    * Provides a simple *function‑calling* mechanism and a lightweight
      **delegation** hook (e.g. forward the query to a cloud LLM).
    """

    def __init__(
        self,
        model_dir: Path,
        tokenizer_dir: Path,
        *,
        delegate_names: Optional[List[str]] = None,
        max_new_tokens: int = 64,
    ) -> None:
        # ───────────────────── model + tokenizer ──────────────────────
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

        self.pipe = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            device_map="auto",
        )

        # ───────────────────── settings & helpers ─────────────────────
        self.max_new_tokens = max_new_tokens
        self.delegate_names = delegate_names or []
        self.tools = self._load_tools()  # make tool registry available

    # ────────────────────────── public API ────────────────────────────
    def process_input(self, user_text: str) -> LlamaOutput:
        """Turn *user_text* into an answer or delegation directive.

        Returns **only** the assistant’s answer string – the prompt is never
        included in the return value, so `service.py` doesn’t need to trim it.
        """
        logging.debug("Processing input: %s", user_text)

        prompt = self._build_prompt(user_text)
        logging.debug("Built prompt: %s", prompt)

        raw_answer = self._generate(prompt)
        logging.debug("Raw model output: %s", raw_answer)

        # ───── check for <functioncall>{...}</functioncall> blocks ─────
        match = _TOOL_REGEX.search(raw_answer)
        if match:
            payload = json.loads(match.group(1).strip())
            name, args = payload.get("name"), payload.get("arguments", {})
            logging.debug("Detected function‑call payload: %s", payload)

            # Simple delegation hook
            if name and name.startswith("delegate_to_"):
                target = name.split("delegate_to_")[-1]
                return LlamaOutput(text="", delegate=True, delegate_target=target)

            # Local tool execution
            if name in self.tools:
                try:
                    result = self.tools[name](**args)
                except Exception as exc:  # noqa: BLE001 – we log & continue
                    logging.exception("Tool '%s' raised", name)
                    result = f"<error>{exc}</error>"

                # Re‑feed the tool result so the model can respond naturally
                follow_up_prompt = (
                    prompt
                    + raw_answer
                    + f"\nFunction `{name}` returned: {result}\nAssistant: "
                )
                final_answer = self._generate(follow_up_prompt)
                return LlamaOutput(text=final_answer.strip(), function_called=True)

        return LlamaOutput(text=raw_answer.strip())

    # ─────────────────────── internal helpers ────────────────────────
    def _generate(self, full_prompt: str) -> str:
        """Helper around `pipeline()` that enforces sane defaults."""
        out = self.pipe(
            full_prompt,
            do_sample=False,            # deterministic; change if you *need* diversity
            max_new_tokens=self.max_new_tokens,
            return_full_text=False,     # only freshly‑generated tokens
            pad_token_id=self.tokenizer.eos_token_id,
            eos_token_id=self.tokenizer.eos_token_id,
        )
        return out[0]["generated_text"]

    def _build_prompt(self, user_text: str) -> str:
        tools_json = json.dumps(self._tools_schema(), indent=2)
        return (
            "You are BetterAlexa. Answer user queries. "
            "If a function/tool is needed, output <functioncall>{JSON}</functioncall>.\n"
            f"Available tools: {tools_json}\n\n"
            f"User: {user_text}\nAssistant: "
        )

    def _load_tools(self) -> Dict[str, Any]:
        """Register built‑in plus delegation pseudo‑tools."""
        registry: Dict[str, Any] = {
            "math_add": lambda a, b: a + b,
        }
        for name in self.delegate_names:
            registry[f"delegate_to_{name}"] = lambda **_: None  # placeholder
        return registry

    def _tools_schema(self) -> List[Dict[str, Any]]:
        schema = [
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
