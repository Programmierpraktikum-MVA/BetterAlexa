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
from function_calling.llama3 import LLama3
import gpu_utils

# Workaround for not using client with audio input, but just typing
no_audio = False

needed_for_whisper = gpu_utils.WHISPER_MEDIUM_FP16_GB + gpu_utils.SAFETY_MARGIN_GB

# Disabled FlashAttention for now, because of GPU compatibility (should be changed for deployment on server; for @Backend)
torch.backends.cuda.enable_flash_sdp(False)        # disable FlashAttention
torch.backends.cuda.enable_mem_efficient_sdp(False) # Has to be deactivate for @GymKiler, due to GPU; Will lead to 15-20% Performance loss. 
torch.backends.cuda.enable_math_sdp(True)          # always allowed



# define model size (tiny, base, medium, large)
WHISPER_MODEL = "medium"

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

# This is the check for GPU VRAM for Whisper 
if gpu_utils.gpu_free_gb() >= needed_for_whisper:
    whisper_device = torch.device("cuda")
    logging.info("Enough VRAM – loading Whisper on GPU")
else:
    whisper_device = torch.device("cpu")
    logging.warning("GPU VRAM < %.1f GB → loading Whisper on CPU",
                    needed_for_whisper)

model  = load_model(WHISPER_MODEL, device=whisper_device)

# also load the llama model
llamaModel = LLama3("Llama-3-8B-function-calling", "https://drive.google.com/drive/folders/1Q-EV7D7pEeYl1On_d2JzxFEB67-KmEm3?usp=sharing", "https://drive.google.com/drive/folders/1RmhIu2FXqwu4TxIQ9GpDtYb_IXWoVd7z?usp=sharing")

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
    if(no_audio == True):
        while True:
            checkQuestion = input("Do you want to ask a question (y/n)?:")
            if checkQuestion.lower() == "y":
                # get question and process it
                question = input("Give me your question: ")
                # check if input is viable
                if question.strip() == "":
                    print("Input cannot be empty. Try again.")
                else:
                    answer = llamaModel.process_input(question)

                    # directly print answer
                    print(answer)
            elif checkQuestion.lower() == "n":
                break
            else:
                print(f"Invalid input '{checkQuestion}'. Use 'y' for yes and 'n' for no. Try again.")
    else:
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
        answer = llamaModel.process_input(transcription_result['text'])

    
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
