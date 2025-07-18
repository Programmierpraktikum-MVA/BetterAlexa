"""
This is the heart if BetterAlexa. 
It uses FastAPI Event-handler to route BetterAlexa traffic to the correct destination. 
"""

import logging
import asyncio, io, os
from enum import Enum, auto
from typing import Dict, List, Optional, Callable, Awaitable
import subprocess
import json
from fastapi.middleware.cors import CORSMiddleware
from database.FastAPI_request_handler import router as zoom_router
import httpx, numpy as np, soundfile as sf
from fastapi import FastAPI, HTTPException, Request, Depends, Security, BackgroundTasks
from fastapi.security.api_key import APIKeyHeader
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, constr, Field
from pathlib import Path
from whisper import load_model  # type: ignore
from function_calling.llama3 import LLama3, LlamaOutput  # updated API
from TTS.api import TTS  # type: ignore
import certifi, ssl
from database.database_wrapper import authenticate_user, get_sensitive_data, set_sensitive_data, get_user_setting, set_user_setting, set_zoom_link, get_zoom_link, get_user_id_by_meeting_id 

logging.basicConfig(level=logging.DEBUG)

# parameters for the LLMs
WHISPER_MODEL_NAME = os.getenv("WHISPER_MODEL", "medium")
LLAMA_MODEL_NAME   = os.getenv("LLAMA_MODEL", "Llama-3-8B-function-calling")
LLAMA_MODEL_DIR = Path(__file__).parent / "function_calling" / "Llama-3-8B-function-calling-model"
LLAMA_TOKENIZER_DIR = Path(__file__).parent / "function_calling" / "Llama-3-8B-function-calling-tokenizer"

# parameters for the Integrations 
# TBD @Backend
TUTORAI_URL   = os.getenv("TUTORAI_URL", "http://108.181.203.191:8006/api/v1/chat")
TUTORAI_TOKEN = os.getenv("101")

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
app.include_router(zoom_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # für Tests, später einschränken!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        model_dir=str(LLAMA_MODEL_DIR),
        tokenizer_dir=str(LLAMA_TOKENIZER_DIR),
    )
    app.state.ttsEN     = TTS(model_name="tts_models/en/vctk/vits", progress_bar=False)
    app.state.ttsDE     = TTS(model_name="tts_models/de/thorsten/tacotron2-DDC", progress_bar=False)
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

# User Registration and Login

class UserCreateRequest(BaseModel):
    user_id: constr = Field(..., min_length=3)
    password: constr = Field(..., min_length=6)

class UserLoginRequest(BaseModel):
    user_id: str
    password: str

class UserSettingRequest(BaseModel):
    key: str = Field(..., min_length=1)
    value: str

class UserSettingGetRequest(BaseModel):
    key: str = Field(..., min_length=1)
class ZoomLinkRequest(BaseModel):
    zoom_link: str

@app.post("/set_zoom_link")
def api_set_zoom_link(request: ZoomLinkRequest, user_id: str = Depends(get_current_user)):
    try:
        set_zoom_link(user_id, request.zoom_link)
        return {"status": "success"}
    except HTTPException as e:
        raise e

@app.get("/get_zoom_link")
def api_get_zoom_link(user_id: str = Depends(get_current_user)):
    try:
        zoom_link = get_zoom_link(user_id)
        if zoom_link is None:
            raise HTTPException(status_code=404, detail="Zoom link not found")
        return {"zoom_link": zoom_link}
    except HTTPException as e:
        raise e
# Endpoints User Settings
@app.post("/set_user_setting")
def api_set_user_setting(request: UserSettingRequest, user_id: str = Depends(get_current_user)):
    try:
        set_user_setting(user_id, request.key, request.value)
        return {"status": "success"}
    except HTTPException as e:
        raise e

@app.post("/get_user_setting")
def api_get_user_setting(request: UserSettingGetRequest, user_id: str = Depends(get_current_user)):
    try:
        value = get_user_setting(user_id, request.key)
        if value is None:
            raise HTTPException(status_code=404, detail="Setting not found")
        return {"value": value}
    except HTTPException as e:
        raise e

@app.post("/register")
def register_user(request: UserCreateRequest):
    from .database.database_wrapper import create_user
    try:
        api_key = create_user(request.user_id, request.password)
        return {"status": "user created", "api_key": api_key}
    except HTTPException as e:
        raise e

@app.post("/login")
def login_user_endpoint(request: UserLoginRequest):
    from .database.database_wrapper import login_user
    import sqlite3
    import os

    DB_PATH = os.path.join(os.path.dirname(__file__), "database", "key_value_store.db")

    try:
        user_id = login_user(request.user_id, request.password)
        # Fetch api_key from DB
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT api_key FROM users WHERE user_id=?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            raise HTTPException(status_code=500, detail="API key not found")
        api_key = row[0]
        return {"user_id": user_id, "api_key": api_key}
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
EDIT: Token not yet implemented.
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
async def pipeline(
    meeting_id: str,
    pcm: np.ndarray,
    pwd: Optional[str] = None,
) -> bytes:
    language, speaker, speed = "en", "p335", 1.0

    # ─── Per-meeting TTS preferences protected by Zoom password ───
    user_id = get_user_id_by_meeting_id(meeting_id)
    if pwd:
        try:
            blob = get_sensitive_data(user_id, "tts_prefs", pwd)
            prefs = json.loads(blob)
            language = prefs.get("language", language)
            speaker  = prefs.get("speaker",  speaker)
            speed    = float(prefs.get("speed", speed))
        except Exception as e:
            logging.warning(f"No or invalid TTS prefs for meeting {user_id}: {e}")

    # ─── Speech-to-text ───
    logging.debug(f"Transcribing PCM audio for meeting {user_id}")
    transcript = app.state.whisper.transcribe(pcm, fp16=False)["text"]
    logging.debug(f"Transcription result: {transcript}")

    # ─── Routing state ───
    state = SESSION_STATE.get(user_id, RouteState.BETTERALEXA)
    logging.debug(f"RouteState for meeting {user_id}: {state}")
    llama: LLama3 = app.state.llama

    if state is RouteState.BETTERALEXA:
        out: LlamaOutput = llama.process_input(transcript)
        logging.debug(f"Llama output: {out}")
        answer = out.text

        if out.delegate:
            target = (out.delegate_target or "tutorai").lower()
            if target == "tutorai":
                SESSION_STATE[user_id] = RouteState.TUTORAI
            else:
                logging.warning(f"Unknown delegate target '{target}', staying in BETTERALEXA")
            logging.debug(f"Delegating to {target}")
            result = await _delegate_call(target, transcript, user_id)
            answer = result.answer
            if result.done:
                SESSION_STATE[user_id] = RouteState.BETTERALEXA

    elif state in STATE_TO_DELEGATE:
        target = STATE_TO_DELEGATE[state]
        logging.debug(f"Ongoing delegation to {target}")
        result = await _delegate_call(target, transcript, user_id)
        answer = result.answer
        if result.done:
            SESSION_STATE[user_id] = RouteState.BETTERALEXA
    else:
        answer = "[testing mode placeholder]"

    # ─── Sanity checks ───
    answer = answer.strip()
    if not answer:
        logging.warning("Empty TTS input detected. Using placeholder response.")
        answer = "Sorry, I didn't catch that. Can you repeat?"
    elif len(answer) > 500:
        logging.warning(f"Excessively long TTS input detected ({len(answer)} chars). Truncating.")
        answer = answer[:500]
    logging.debug(f"TTS input: {answer}")

    # ─── Text-to-speech ───
    logging.debug(f"languageTTS =={language}")
    if language == "de": 
        wav_np = app.state.ttsDE.tts(
            text=answer,
            speaker=speaker,
        )
    else:
        wav_np = app.state.ttsEN.tts(
            text=answer,
        )
    buf = io.BytesIO()
    sf.write(
        buf,
        wav_np,
        samplerate=app.state.tts.synthesizer.output_sample_rate,
        format="WAV",
    )
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
async def stream(payload: StreamPayload
                 ):
    logging.debug(f"Received request")
    pwd: Optional[str] = None
    try:
        response = await app.state.httpx.get(
            f"http://127.0.0.1:8000/zoom/password/{payload.meeting_id}",
            timeout=2.0,
        )
        if response.status_code == 200:
            pwd = response.json()["password"]
    except httpx.HTTPError as exc:
        logging.warning(f"Could not reach /zoom/password endpoint: {exc}")

    try:
        wav = await pipeline(payload.meeting_id, np.array(payload.pcm, dtype=np.float32), pwd)
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
async def handle_zoom_link(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    link = data.get("link")
    logging.debug(f"Received link: {link}")

    current_dir = os.path.dirname(os.path.abspath(__file__))
    zoom_bot_dir = os.path.join(current_dir, os.path.abspath("zoom_bot/repo_zoom_sdk/zoomBot-main"))
    config_file_path = os.path.join(zoom_bot_dir, "config.txt")

    # get the meeting id and pwd from the link
    meeting_number, pwd = parse_link(link)

    # edit config.txt from zoomBot for our given link
    # Read lines
    with open(config_file_path, "r") as f:
        lines = f.readlines()

    # Overwrite Meeting_number and meeting_password, making sure to add '\n'
    lines[0] = f'meeting_number: "{meeting_number}"\n'
    lines[3] = f'meeting_password: "{pwd}"\n'

    # Write back
    with open(config_file_path, "w") as f:
        f.writelines(lines)

    # compile and execute zoom bot 
    
    zoom_build_dir = os.path.join(current_dir, os.path.abspath("zoom_bot/repo_zoom_sdk/zoomBot-main/build"))
    # Ensure the build directory exists
    os.makedirs(zoom_build_dir, exist_ok=True)

    # Add the background task
    background_tasks.add_task(run_zoom_bot, zoom_bot_dir, zoom_build_dir)

    return {"status": "ok"}

def run_zoom_bot(zoom_bot_dir, zoom_build_dir):
    logging.debug(f"Compiling Zoom Bot from dir: {zoom_build_dir}")
    subprocess.run(['cmake', '..'], cwd=zoom_build_dir, check=True)
    subprocess.run(['cmake', '--build', '.'], cwd=zoom_build_dir, check=True)
    subprocess.run(['./bin/meetingSDK'], cwd=zoom_bot_dir, check=True)

def parse_link(link: str):
    """
    Takes a zoom meeting invite link and returns the included meeting id and password.
    
    Args:
        link (str): The full zoom invite link.

    Returns:
        meeting_id: The Meeting ID for the zoom meeting.
        pwd: The Password for the zoom meeting.
    """
    parts = link.split("/")
    meeting_id, pwd = parts[4].split("?")
    #meeting_id = meeting_id[0:3] + ' ' + meeting_id[3:7] + ' ' + meeting_id[7:10]

    end = len(pwd) -2
    pwd = pwd[4:end]
    return meeting_id,pwd
