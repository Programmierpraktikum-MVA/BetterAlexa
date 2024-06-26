from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from gtts import gTTS
import os

app = FastAPI()


@app.post("/text-to-speech/")
async def text_to_speech(text: str):
    if not text:
        raise HTTPException(status_code=400, detail="empty text not allowed")

    tts = gTTS(text)
    file_path = "output.mp3"
    tts.save(file_path)

    return FileResponse(file_path, media_type='audio/mpeg', filename="output.mp3")


if __name__ == "__main__":
    import uvicorn

    # 1:  command to run : uvicorn ttsService:app --reload
    uvicorn.run(app, host="0.0.0.0", port=8000)

    #2: head to the 127.0.... as shown
    #3: enter text
    #4: execute
    #5: download output file with the read out text using gTTS

