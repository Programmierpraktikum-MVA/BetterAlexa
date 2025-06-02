
"""Llama‑3 wrapper with structured output and **generic delegation**.
Pass `delegate_names=["tutorai", "anthropic", ...]` to register pseudo tools.
"""
from __future__ import annotations
from pathlib import Path
import json, re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

_TOOL_REGEX = re.compile(r"<functioncall>(.*?)</functioncall>", re.DOTALL)

@dataclass
class LlamaOutput:
    text: str
    delegate: bool = False
    delegate_target: Optional[str] = None
    function_called: bool = False

class LLama3:
    def __init__(self, model_dir: Path, tokenizer_dir: Path, delegate_names=None):
        self.tokenizer = AutoTokenizer.from_pretrained(
            tokenizer_dir, local_files_only=True
        )
        self.model = AutoModelForCausalLM.from_pretrained(
            model_dir,
            torch_dtype=torch.float16,
            device_map="auto",
            local_files_only=True,
        )
        self.delegate_names = delegate_names or []
        self.pipe = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            device_map="auto",
            torch_dtype=torch.float16,
        )

    # ────────────────── public ──────────────────
    def process_input(self, user_text: str) -> LlamaOutput:
        chat = self._build_prompt(user_text)
        raw = self.pipe(chat, do_sample=True, temperature=0.7)[0]["generated_text"][len(chat):]

        m = _TOOL_REGEX.search(raw)
        if m:
            payload = json.loads(m.group(1).strip())
            name, args = payload.get("name"), payload.get("arguments", {})
            if name and name.startswith("delegate_to_"):
                target = name.split("delegate_to_")[-1]
                return LlamaOutput(text="", delegate=True, delegate_target=target)
            if name in self.tools:
                try:
                    result = self.tools[name](**args)
                except Exception as e:
                    result = f"<error>{e}</error>"
                chat += raw + f"\nFunction `{name}` returned: {result}"
                final = self.pipe(chat, do_sample=False, temperature=0.2)[0]["generated_text"][len(chat):]
                return LlamaOutput(text=final.strip(), function_called=True)

        return LlamaOutput(text=raw.strip())

    # ────────────────── internals ───────────────
    def _build_prompt(self, user_text: str) -> str:
        tools_json = json.dumps(self._tools_schema(), indent=2)
        return (
            "You are BetterAlexa. Answer user queries. "
            "If a function/tool is needed, output <functioncall>{JSON}</functioncall>.\n" \
            f"Available tools: {tools_json}\n\n" \
            f"User: {user_text}\nAssistant: "
        )

    def _load_tools(self) -> Dict[str, Any]:
        registry: Dict[str, Any] = {}
        def add(a: int, b: int) -> int:
            return a + b
        registry["math_add"] = add
        # pseudo delegate tools
        for name in self.delegate_names:
            registry[f"delegate_to_{name}"] = lambda **_: None
        return registry

    def _tools_schema(self) -> List[Dict[str, Any]]:
        schema = [{"name": "math_add", "description": "Add two integers", "parameters": {"a": "int", "b": "int"}}]
        schema += [{"name": f"delegate_to_{n}", "description": f"Delegate to {n}", "parameters": {}} for n in self.delegate_names]
        return schema
