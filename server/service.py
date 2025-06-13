"""
This is the heart if BetterAlexa. 
It uses FastAPI Event-handler to route BetterAlexa traffic to the correct destination. 
"""

import logging
import asyncio, io, os
from enum import Enum, auto
from typing import Dict, List, Optional, Callable, Awaitable

import httpx, numpy as np, soundfile as sf
from fastapi import FastAPI, HTTPException, Request, Depends, Security
from fastapi.security.api_key import APIKeyHeader
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from pathlib import Path
from whisper import load_model  # type: ignore
from function_calling.llama3 import LLama3, LlamaOutput  # updated API
from TTS.api import TTS  # type: ignore
import certifi, ssl
from server.database.database_wrapper import authenticate_user, get_sensitive_data, set_sensitive_data

logging.basicConfig(level=logging.DEBUG)

# parameters for the LLMs
WHISPER_MODEL_NAME = os.getenv("WHISPER_MODEL", "medium")
LLAMA_MODEL_NAME   = os.getenv("LLAMA_MODEL", "Llama-3-8B-function-calling")
LLAMA_MODEL_DIR = Path(__file__).parent / "function_calling" / "Llama-3-8B-function-calling-model"
LLAMA_TOKENIZER_DIR = Path(__file__).parent / "function_calling" / "Llama-3-8B-function-calling-tokenizer"

# parameters for the Integrations 
# TBD @Backend
TUTORAI_URL   = os.getenv("TUTORAI_URL", "https://tutor.ai/api/v1/chat")
TUTORAI_TOKEN = os.getenv("TUTORAI_TOKEN")

# The routing states that BetterAlexa uses for traffic.
class RouteState(Enum):
    BETTERALEXA = auto()
    DELEGATE    = auto()
    TESTING     = auto()
    TUTORAI     = auto()

# per‑meeting state stores
SESSION_STATE: Dict[str, RouteState]       = {}
SESSION_DELEGATE: Dict[str, Optional[str]] = {}   # e.g. {"m42": "tutorai"}

# silencing of "loud" libraries for debugging
for noisy in ["TTS", "transformers", "urllib3", "numba"]:
    logging.getLogger(noisy).setLevel(logging.WARNING)

# ─────────────────────── FastAPI setup ──────────────────────
app = FastAPI(title="BetterAlexa Core", version="0.6")

# A semaphore for limiting how many parallel TutorAI conversations BetterAlexa can have
_tutor_sem = asyncio.Semaphore(int(os.getenv("TUTOR_CONCURRENCY", 5)))

"""
Everything that happens on Server startup 
Loads needed LLMs (Whisper, Llama, TTS)
Creates a HTTP Client for communication with Integrations (TutorAI, ...)
"""
@app.on_event("startup")
async def _startup() -> None:
    import torch
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    app.state.whisper = load_model(WHISPER_MODEL_NAME, device=device)
    app.state.llama = LLama3(
        model_dir=LLAMA_MODEL_DIR,
        tokenizer_dir=LLAMA_TOKENIZER_DIR,
    )
    app.state.tts     = TTS(model_name="tts_models/en/vctk/vits", progress_bar=False)
    ctx = ssl.create_default_context(cafile=certifi.where())
    app.state.httpx   = httpx.AsyncClient(http2=True, timeout=10, verify=ctx)

@app.on_event("shutdown")
async def _shutdown() -> None:
    await app.state.httpx.aclose()


# Database
API_KEY_HEADER = APIKeyHeader(name="X-API-Key")
def get_current_user(api_key: str = Security(API_KEY_HEADER)):
    try:
        user_id = authenticate_user(api_key)
        return user_id
    except HTTPException as e:
        raise e

# Request-Modelle für sichere Daten
class SensitiveDataRequest(BaseModel):
    key: str
    password: str

class SensitiveDataSetRequest(BaseModel):
    key: str
    value: str
    password: str

# Endpoint: Sensible Daten lesen
@app.post("/get_sensitive_data")
def read_sensitive_data(request: SensitiveDataRequest, user_id: str = Depends(get_current_user)):
    try:
        value = get_sensitive_data(user_id, request.key, request.password)
        return {"value": value}
    except HTTPException as e:
        raise e

# Endpoint: Sensible Daten schreiben
@app.post("/set_sensitive_data")
def write_sensitive_data(request: SensitiveDataSetRequest, user_id: str = Depends(get_current_user)):
    try:
        set_sensitive_data(user_id, request.key, request.value, request.password)
        return {"status": "success"}
    except HTTPException as e:
        raise e
    
# ─────────────────── delegate handlers registry ─────────────
DelegateHandler = Callable[[str, str], Awaitable["DelegateResult"]]  # (query, meeting_id) -> answer text & done bool maybe

class DelegateResult(BaseModel):
    answer: str
    done: bool = False

"""
Builds the defined JSON formatted Payload
Sends request to TutorAI and returns answer and "done" field for state within pipeline
uses TUTORAI_TOKEN from environment variables for authentication
"""
async def _call_tutorai(query: str, meeting: str) -> DelegateResult:
    payload = {"query": query}
    #semaphore to limit concurrent requests to TutorAI
    async with _tutor_sem:
        # Send request to TutorAI and await response
        r = await app.state.httpx.post(
            TUTORAI_URL,
            json=payload,
            headers={"Authorization": f"Bearer {TUTORAI_TOKEN}"}
        )
    if r.status_code != 200:
        raise HTTPException(status_code=502, detail="TutorAI upstream error")
    
    # Checks if TUTORAI_TOKEN is contained in response header
    auth_header = r.headers.get("Authorization")
    if auth_header:
        if not auth_header.startswith("Bearer "):
            logging.warning("Invalid Authorization header format in response")
            raise HTTPException(status_code=502, detail="Invalid auth response format")
        
        # Extract and validate token
        response_token = auth_header[7:]  # Remove "Bearer " prefix
        if not TUTORAI_TOKEN == response_token:
            logging.error("Invalid response token received")
            raise HTTPException(status_code=502, detail="Invalid response authentication")
        
        logging.debug("Response authentication verified")
    else:
        logging.warning("No Authorization header in TutorAI response")

    #extract and return the answer and done status
    data = r.json()
    return DelegateResult(answer=data.get("answer", ""), done=data.get("done", False))


DELEGATE_HANDLERS: Dict[str, DelegateHandler] = {
    "tutorai": _call_tutorai,
}

STATE_TO_DELEGATE = {
    RouteState.TUTORAI: "tutorai",
}

"""
This is the main pipeline.  
It receivevs a meeting ID and the corresponding audio stream. It then  
transforms it into text (Whisper),
answers (Llama or Integration, depending on state),
and turns the answer into speech (TTS).
"""
async def pipeline(meeting: str, pcm: np.ndarray) -> bytes:
    logging.debug(f"Transcribing PCM audio for meeting {meeting}")
    whisper = app.state.whisper
    transcript = whisper.transcribe(pcm, fp16=False)["text"]
    logging.debug(f"Transcription result: {transcript}")
    state = SESSION_STATE.get(meeting, RouteState.BETTERALEXA)
    llama: LLama3 = app.state.llama
    logging.debug(f"RouteState for meeting {meeting}: {state}")

    # 1) Local handling
    if state is RouteState.BETTERALEXA:
        out: LlamaOutput = llama.process_input(transcript)
        logging.debug(f"Llama output: {out}")
        answer = out.text
        if out.delegate:
            target = (out.delegate_target or "tutorai").lower()
            if target == "tutorai":
                SESSION_STATE[meeting] = RouteState.TUTORAI
            else:
                logging.warning(f"Unknown delegate target '{target}', staying in BETTERALEXA")
            logging.debug(f"Delegating to {target}")
            result = await _delegate_call(target, transcript, meeting)
            answer = result.answer
            if result.done:
                SESSION_STATE[meeting] = RouteState.BETTERALEXA

    # 2) Ongoing delegation
    elif state in STATE_TO_DELEGATE:
        target = STATE_TO_DELEGATE[state]
        logging.debug(f"Ongoing delegation to {target}")
        result = await _delegate_call(target, transcript, meeting)
        answer = result.answer
        if result.done:
            SESSION_STATE[meeting] = RouteState.BETTERALEXA

    # 3) Testing fallback
    else:
        answer = "[testing mode placeholder]"

    answer = answer.strip()
    if not answer:
        logging.warning("Empty TTS input detected. Using placeholder response.")
        answer = "Sorry, I didn't catch that. Can you repeat?"
    elif len(answer) > 500:  # arbitrary length check
        logging.warning(f"Excessively long TTS input detected ({len(answer)} chars). Truncating.")
        answer = answer[:500]
    logging.debug(f"TTS input: {answer}")
    # @DB The "speaker" is where you might use the database. Talk to @Winter for other things that might be costumized for the TTS. 
    # TTS
    wav_np = app.state.tts.tts(text=answer, speaker="p335")
    buf = io.BytesIO()
    sf.write(buf, wav_np, samplerate=app.state.tts.synthesizer.output_sample_rate, format="WAV")
    buf.seek(0)
    logging.debug(f"Returning WAV bytes of length: {buf.getbuffer().nbytes}")
    return buf.read()

async def _delegate_call(target: Optional[str], query: str, meeting: str) -> DelegateResult:
    if not target or target not in DELEGATE_HANDLERS:
        return DelegateResult(answer="[delegate target not available]", done=True)
    return await DELEGATE_HANDLERS[target](query, meeting)



class StreamPayload(BaseModel):
    meeting_id: str
    pcm: List[float]

"""
This is the Endpoint for Traffic. 
It takes an audio-stream and meeting-id as input and outputs the answer-audio stream.
"""
@app.post("/api/v1/stream", response_class=StreamingResponse)
async def stream(payload: StreamPayload):
    logging.debug(f"Received request")
    try:
        wav = await pipeline(payload.meeting_id, np.array(payload.pcm, dtype=np.float32))
        logging.debug(f"Generated audio size: {len(wav)} bytes")
    except Exception as e:
        logging.exception(f"Error in pipeline processing: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    async def audio_streamer(data: bytes, chunk_size=4096):
        for i in range(0, len(data), chunk_size):
            yield data[i:i + chunk_size]

    return StreamingResponse(audio_streamer(wav), media_type="audio/wav")

"""
This is the Endpoint for Discord Integration handling.
It takes (for now) a zoom invite link and forwards this to the zoombot 
"""
@app.post("/handle_zoom_link")
async def handle_zoom_link(request: Request):
    data = await request.json()
    link = data.get("link")
    # TODO: forward the link to zoombot and handle response
    return {"status": "ok"}