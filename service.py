import logging
import torch
from os import path, remove
from time import time
from warnings import filterwarnings
from whisper import load_model
from fastapi import FastAPI, UploadFile
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse, FileResponse
from main import process_input
from llama3 import LLama3

# define model size (tiny, base, medium, large)
WHISPER_MODEL = "base"

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Suppress specific warnings (FP16)
filterwarnings("ignore", category=UserWarning, message="FP16 is not supported on CPU; using FP32 instead")

logging.info("Loading finished - starting server")
app = FastAPI(
    title="Whisper API",
    description="""Whisper API""",
    version="0.1"
)
origins = ["*"]

logging.info(f"Loading the {WHISPER_MODEL} Whisper model and LLama model!")
# whisper model on cpu because of gpu memory issues
model = load_model(WHISPER_MODEL, device=torch.device("cpu"))

# also load the llama model
with open('functions.json', 'r') as file:
        functions = file.read()
llamaModel = LLama3("Llama-3-8B-function-calling", functions, "https://drive.google.com/drive/folders/1Q-EV7D7pEeYl1On_d2JzxFEB67-KmEm3?usp=sharing")

logging.info("Whisper and LLama model loaded!")

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


@app.get("/")
def swagger_documentation():
    return RedirectResponse(url='/docs')


@app.post("/whisper")
async def whisper(file: UploadFile):
    # save incoming audio file
    temp_filename = f"TempFile_{time()}.wav"
    with open(temp_filename, 'wb') as temp_file:
        temp_file.write(await file.read())

    # transcribe audio file
    current_time = time()
    transcription_result = model.transcribe(temp_filename)
    whisper_time = time() - current_time
    remove(temp_filename)
    print(f"Transcription result: {transcription_result['text']}")

    answer = process_input(llamaModel, transcription_result['text'])
    
    file_path = path.join(path.dirname(path.abspath(__file__)), "transcription.txt")
    with open(file_path, "w", encoding="utf-8") as txt:
        txt.write(answer)

    current_time = time()
    tts_time = time() - current_time

    # send response with meta-data in headers
    return FileResponse(
        path=file_path,
        media_type="text/plain",
        headers={
            "X-Language": transcription_result["language"],
            "Time-Whisper": str(whisper_time),
            "Time-TTS": str(tts_time)
        }
    )
