import logging
import torch
from whisper import load_model
from fastapi import FastAPI
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware
from function_calling.llama3 import LLama3
import gpu_utils

# Speichergrenze für Whisper-Modell
needed_for_whisper = gpu_utils.WHISPER_MEDIUM_FP16_GB + gpu_utils.SAFETY_MARGIN_GB

# FlashAttention deaktivieren
torch.backends.cuda.enable_flash_sdp(False)
torch.backends.cuda.enable_mem_efficient_sdp(False)
torch.backends.cuda.enable_math_sdp(True)

# Whisper-Modellgröße
WHISPER_MODEL = "medium"

# Logging konfigurieren
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Warnungen unterdrücken
from warnings import filterwarnings
filterwarnings("ignore", category=UserWarning, message="FP16 is not supported on CPU; using FP32 instead")

logging.info("Loading finished - starting server")
app = FastAPI(
    title="Whisper API",
    description="""Whisper API""",
    version="0.1"
)
origins = ["*"]

logging.info(f"Loading the {WHISPER_MODEL} Whisper model and LLama model!")

# GPU prüfen
if gpu_utils.gpu_free_gb() >= needed_for_whisper:
    whisper_device = torch.device("cuda")
    logging.info("Enough VRAM – loading Whisper on GPU")
else:
    whisper_device = torch.device("cpu")
    logging.warning("GPU VRAM < %.1f GB → loading Whisper on CPU",
                    needed_for_whisper)

# Modelle laden
model = load_model(WHISPER_MODEL, device=whisper_device)
llamaModel = LLama3(
    "Llama-3-8B-function-calling",
    "https://drive.google.com/drive/folders/1Q-EV7D7pEeYl1On_d2JzxFEB67-KmEm3?usp=sharing",
    "https://drive.google.com/drive/folders/1RmhIu2FXqwu4TxIQ9GpDtYb_IXWoVd7z?usp=sharing"
)

logging.info("Whisper and LLama model loaded!")

# CORS konfigurieren
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Query(BaseModel):
    query: str

logging.info("All complete - ready for traffic")

# Transkriptions-Funktion
async def transcribe_response(audio_np):
    transcription_result = model.transcribe(audio_np, fp16=False)
    print(f"Transcription result: {transcription_result['text']}")
    answer = llamaModel.process_input(transcription_result['text'])
    return answer
