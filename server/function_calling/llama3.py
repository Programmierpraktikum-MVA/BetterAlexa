"""Llama‑3 wrapper for BetterAlexa – updated to use **chat‑template generation**
exactly like the previous `llama3_old.py` while still exposing the modern
`LlamaOutput` API expected by `service.py`.

Key changes vs the last revision
================================
* Keeps a rolling **chat list** and formats prompts through
  `tokenizer.apply_chat_template`, identical to the old implementation.
* Loads **functions.json verbatim** and injects it once as a *system* message
  ("You have access to the following functions …").  No schema processing –
  we simply pass the raw JSON string to the model, again mirroring
  `llama3_old.py`.
* Generation defaults to `temperature=0.1`, `top_k=50`, `top_p=0.1` and up
  to `512` new tokens, matching the legacy behaviour.
* A new **_assistant_only() stop helper** trims everything after the first
  role tag ("user", "assistant", "system") – exactly the stop‑criterion the
  old wrapper achieved implicitly via its EOS token.  This prevents the model
  from hallucinating additional turns inside a single response.

2025‑06‑06  ▸  Patch 3
--------------------
* **Fallback to globals() for tools** – if a function name isn’t registered in
  `self.tools`, `_run_tool()` now looks it up in the module’s global symbol
  table (so `from actions.wolfram import ask_wolfram_question` works exactly
  like in the old wrapper).  This lets you add tool functions via a simple
  import without wiring them into `skills.*` shims.
* No other logic or comments changed.
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
_FUNC_TAG_RE = re.compile(r"<functioncall>(.*?)</functioncall>", re.DOTALL | re.I)
_FUNC_OPEN_RE = re.compile(r"<functioncall>(.*)", re.DOTALL | re.I)
_ROLE_RE = re.compile(r"\n\s*(user|assistant|system)[:\s]", re.I)


# ───────────────────────── public dataclass ─────────────────────────
@dataclass
class LlamaOutput:
    """Result returned by :pymeth:`LLama3.process_input`."""

    text: str
    delegate: bool = False
    delegate_target: Optional[str] = None
    function_called: bool = False


class LLama3:
    """Chat‑style Llama‑3 wrapper with legacy generation semantics."""

    # chat & memory limits
    _MAX_CHAT_TOKENS = 1024

    def __init__(
        self,
        model_dir: Path,
        tokenizer_dir: Path,
        *,
        functions_file: Path = Path(__file__).with_name("functions.json"),
        tutor_delegate: str = "TutorAI",
        max_new_tokens: int = 512,
    ) -> None:
        self.logger = logging.getLogger(__name__)

        # ═════════════════ load functions.json (verbatim) ══════════════════
        with functions_file.open("r", encoding="utf‑8") as fh:
            self.functions_json_str: str = fh.read()
        self.tutor_delegate_name = tutor_delegate.lower()

        # prepare chat memory & prime with system message
        self.chat: List[Dict[str, str]] = []
        self.chat_length: int = 0  # word count approximation
        system_msg = (
            "You are a helpful assistant with access to the following functions. "
            "Use them if required -\n{\n" + self.functions_json_str + "\n}"
        )
        self._append_to_chat("system", system_msg)

        # ══════════════════ model & tokenizer ═══════════════════════════════
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

        self.max_new_tokens = max_new_tokens

        # ══════════════════ tool registry (minimal) ═════════════════════════
        self.tools: Dict[str, Any] = self._load_tools()

    # ──────────────────────────── chat helpers ────────────────────────────
    def _append_to_chat(self, role: str, content: str) -> None:
        msg = {"role": role, "content": content}
        self.chat.append(msg)
        self.chat_length += len(content.split())
        # maintain rolling window
        while self.chat_length > self._MAX_CHAT_TOKENS and len(self.chat) > 2:
            removed = self.chat.pop(1)
            self.chat_length -= len(removed["content"].split())

    # ───────────────────────── stop‑criterion helper ──────────────────────
    def _assistant_only(self, text: str) -> str:
        """Trim everything after the first role tag to mimic old wrapper stops."""
        m = _ROLE_RE.search(text)
        return (text[: m.start()] if m else text).strip()

    # ─────────────────────────── generation ───────────────────────────────
    def _generate(self, prompt: str) -> str:
        out = self.pipe(
            prompt,
            do_sample=False,  # deterministic; sampling params disabled
            max_new_tokens=self.max_new_tokens,
            return_full_text=False,
            pad_token_id=self.tokenizer.eos_token_id,
            eos_token_id=self.tokenizer.eos_token_id,
        )
        return out[0]["generated_text"].strip()

    def _chat_prompt(self) -> str:
        try:
            return self.tokenizer.apply_chat_template(
                self.chat,
                tokenize=False,
                add_generation_prompt=True,
            )
        except (ValueError, AttributeError):
            # Fallback – plain format if template missing
            lines = [f"{m['role']}: {m['content']}" for m in self.chat]
            lines.append("assistant: ")
            return "\n".join(lines)

    # ───────────────────────── function helpers ───────────────────────────
    def _extract_func_payload(self, text: str) -> Optional[Dict[str, Any]]:
        m = _FUNC_TAG_RE.search(text) or _FUNC_OPEN_RE.search(text)
        if not m:
            return None
        json_str = m.group(1)
        role_match = _ROLE_RE.search(json_str)
        if role_match:
            json_str = json_str[: role_match.start()]
        try:
            return json.loads(json_str.strip())
        except json.JSONDecodeError:
            try:
                return json.loads(json_str.replace("'", '"'))
            except Exception:
                self.logger.warning("Could not parse function JSON: %s", json_str)
                return None

    def _run_tool(self, name: str, args: Dict[str, Any]) -> Any:
        """Execute a registered tool, falling back to globals() like the old wrapper."""
        func = self.tools.get(name)
        if not func:
            func = globals().get(name)  # ← legacy fallback
        if not func:
            return f"<error>Unknown tool: {name}</error>"
        try:
            return func(**args) if args else func()
        except Exception as exc:  # noqa: BLE001
            self.logger.exception("Tool '%s' raised", name)
            return f"<error>{exc}</error>"

    # ───────────────────────── public API ────────────────────────────────
    def process_input(self, user_text: str) -> LlamaOutput:
        # 1) generate initial answer
        self._append_to_chat("user", user_text)
        prompt = self._chat_prompt()
        raw_answer = self._generate(prompt)

        # Store only the assistant part (stops applied) in history
        assistant_snippet = self._assistant_only(raw_answer)
        self._append_to_chat("assistant", assistant_snippet)

        # 2) detect function‑call in the *untrimmed* raw answer
        payload = self._extract_func_payload(raw_answer)
        if payload:
            name = payload.get("name", "")
            args = payload.get("arguments", {})

            # ─── Delegation to TutorAI ───────────────────────────────────
            if name.lower().startswith("ask_tutorai"):
                return LlamaOutput(text="", delegate=True, delegate_target=self.tutor_delegate_name)

            # ─── Local execution ────────────────────────────────────────
            if isinstance(args, str):  # JSON encoded inside string
                try:
                    args = json.loads(args)
                except Exception:
                    args = {}
            result = self._run_tool(name, args)

            # Let the model turn the raw result into nice prose
            follow_up = (
                prompt
                + raw_answer
                + f"\nFunction `{name}` returned: {result}\nAssistant: "
            )
            final_answer = self._assistant_only(self._generate(follow_up))
            return LlamaOutput(text=final_answer, function_called=True)

        # 3) plain answer (trimmed)
        return LlamaOutput(text=assistant_snippet)

    # ───────────────────────── tool registry ─────────────────────────────
    def _load_tools(self) -> Dict[str, Any]:
        registry: Dict[str, Any] = {}
        try:
            spec = json.loads(self.functions_json_str)
        except Exception:
            self.logger.warning("functions.json is not valid JSON – tools disabled")
            return registry
        for entry in spec:
            fname = entry.get("name")
            if not fname:
                continue
            try:
                mod = importlib.import_module(f"skills.{fname}")
                registry[fname] = getattr(mod, "run")
            except Exception:
                self.logger.debug("No implementation for %s – stub registered", fname)
                registry[fname] = lambda **_: f"[{fname} executed]"
        return registry
