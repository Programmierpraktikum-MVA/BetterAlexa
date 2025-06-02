
"""FastAPI core – now with a **generic delegation framework**.

* `RouteState` has three values: BETTERALEXA, DELEGATE, TESTING
* For DELEGATE we keep a per‑meeting `delegate_target` (e.g. "tutorai",
  "anthropic", ...).  Adding a new cloud LLM means:
    1) register an async handler in `DELEGATE_HANDLERS`
    2) expose a pseudo‑tool `delegate_to_<name>` in llama3.py
That's it – no more enum edits.
"""
from __future__ import annotations

import asyncio, io, os
from enum import Enum, auto
from typing import Dict, List, Optional, Callable, Awaitable

import httpx, numpy as np, soundfile as sf
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from whisper import load_model  # type: ignore
from function_calling.llama3 import LLama3, LlamaOutput  # updated API
from TTS.api import TTS  # type: ignore

# ────────────────────────── config ──────────────────────────
WHISPER_MODEL_NAME = os.getenv("WHISPER_MODEL", "medium")
LLAMA_MODEL_NAME   = os.getenv("LLAMA_MODEL", "Llama-3-8B-function-calling")

# TutorAI creds (first delegate target)
TUTORAI_URL   = os.getenv("TUTORAI_URL", "https://tutor.ai/api/v1/chat")
TUTORAI_TOKEN = os.getenv("TUTORAI_TOKEN", "REPLACE_ME")

# ────────────────────────── FSM ─────────────────────────────
class RouteState(Enum):
    BETTERALEXA = auto()
    DELEGATE    = auto()
    TESTING     = auto()

# per‑meeting state stores
SESSION_STATE: Dict[str, RouteState]      = {}
SESSION_DELEGATE: Dict[str, Optional[str]] = {}   # e.g. {"m42": "tutorai"}

# ─────────────────────── FastAPI setup ──────────────────────
app = FastAPI(title="BetterAlexa Core", version="0.6")
_tutor_sem = asyncio.Semaphore(int(os.getenv("TUTOR_CONCURRENCY", 5)))

@app.on_event("startup")
async def _startup() -> None:
    import torch
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    app.state.whisper = load_model(WHISPER_MODEL_NAME, device=device)
    app.state.llama   = LLama3(LLAMA_MODEL_NAME, delegate_names=["tutorai"])  # pass known delegates
    app.state.tts     = TTS(model_name="tts_models/en/vctk/vits", progress_bar=False)
    app.state.httpx   = httpx.AsyncClient(http2=True, timeout=10)

@app.on_event("shutdown")
async def _shutdown() -> None:
    await app.state.httpx.aclose()

# ─────────────────── delegate handlers registry ─────────────
DelegateHandler = Callable[[str, str], Awaitable[str]]  # (query, meeting_id) -> answer text & done bool maybe

class DelegateResult(BaseModel):
    answer: str
    done: bool = False

async def _call_tutorai(query: str, meeting: str) -> DelegateResult:
    payload = {"client_id": meeting, "conversation_id": meeting, "query": query}
    async with _tutor_sem:
        r = await app.state.httpx.post(TUTORAI_URL, json=payload, headers={"Authorization": f"Bearer {TUTORAI_TOKEN}"})
    if r.status_code != 200:
        raise HTTPException(status_code=502, detail="TutorAI upstream error")
    data = r.json()
    return DelegateResult(answer=data.get("answer", ""), done=data.get("done", False))

DELEGATE_HANDLERS: Dict[str, DelegateHandler] = {
    "tutorai": _call_tutorai,
    # "anthropic": _call_anthropic,  # add later
}

# ────────────────────── main pipeline ───────────────────────
async def pipeline(meeting: str, pcm: np.ndarray) -> bytes:
    whisper = app.state.whisper
    transcript = whisper.transcribe(pcm, fp16=False)["text"]

    state = SESSION_STATE.get(meeting, RouteState.BETTERALEXA)
    llama: LLama3 = app.state.llama

    # 1) Local handling
    if state is RouteState.BETTERALEXA:
        out: LlamaOutput = llama.process_input(transcript)
        answer = out.text
        if out.delegate:
            target = out.delegate_target or "tutorai"
            SESSION_STATE[meeting] = RouteState.DELEGATE
            SESSION_DELEGATE[meeting] = target
            result = await _delegate_call(target, transcript, meeting)
            answer = result.answer
            if result.done:
                SESSION_STATE[meeting] = RouteState.BETTERALEXA
                SESSION_DELEGATE.pop(meeting, None)

    # 2) Ongoing delegation
    elif state is RouteState.DELEGATE:
        target = SESSION_DELEGATE.get(meeting)
        result = await _delegate_call(target, transcript, meeting)
        answer = result.answer
        if result.done:
            SESSION_STATE[meeting] = RouteState.BETTERALEXA
            SESSION_DELEGATE.pop(meeting, None)

    # 3) Testing fallback
    else:
        answer = "[testing mode placeholder]"

    # TTS
    wav_np = app.state.tts.tts(text=answer, speaker="p335")
    buf = io.BytesIO()
    sf.write(buf, wav_np, samplerate=app.state.tts.synthesizer.output_sample_rate, format="WAV")
    buf.seek(0)
    return buf.read()

async def _delegate_call(target: Optional[str], query: str, meeting: str) -> DelegateResult:
    if not target or target not in DELEGATE_HANDLERS:
        return DelegateResult(answer="[delegate target not available]", done=True)
    return await DELEGATE_HANDLERS[target](query, meeting)

# ─────────────────────── HTTP endpoint ──────────────────────
class StreamPayload(BaseModel):
    meeting_id: str
    pcm: List[float]

@app.post("/api/v1/stream", response_class=StreamingResponse)
async def stream(payload: StreamPayload):
    wav = await pipeline(payload.meeting_id, np.array(payload.pcm, dtype=np.float32))
    async def it(d: bytes, n=4096):
        for i in range(0, len(d), n):
            yield d[i:i+n]
    return StreamingResponse(it(wav), media_type="audio/wav")

