import logging
from time import time
from os import path, remove
from warnings import filterwarnings
from whisper import load_model
from fastapi import FastAPI, UploadFile
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse, FileResponse
from gtts import gTTS

WHISPER_MODEL = "tiny"

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Suppress specific warnings (FP16)
filterwarnings("ignore", category=UserWarning, message="FP16 is not supported on CPU; using FP32 instead")

logging.info("Loading finished - starting server")
app = FastAPI(
    title="S2T & T2S API",
    description="""Whisper API""",
    version="0.1"
)
origins = ["*"]

logging.info(f"Loading the {WHISPER_MODEL} Whisper model")
# whisper model on cpu because of gpu memory issues
model = load_model(WHISPER_MODEL)

logging.info("Whisper model loaded!")

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

@app.post("/text-to-speech/")
async def text_to_speech(text: str):
    if not text:
        raise HTTPException(status_code=400, detail="empty text not allowed")

    tts = gTTS(text)
    file_path = "output.mp3"
    tts.save(file_path)

    return FileResponse(file_path, media_type='audio/mpeg', filename="output.mp3")

@app.post("/whisper")
async def whisper(file: UploadFile):
    # save incoming audio file
    temp_filename = f"TempFile_{time()}.wav"
    with open(temp_filename, 'wb') as temp_file:
        temp_file.write(await file.read())

    # transcribe audio file
    transcription_result = model.transcribe(temp_filename)
    remove(temp_filename)
    print(f"Transcription result: {transcription_result['text']}")

    # send transcript as response
    return {"message": transcription_result['text']}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)
