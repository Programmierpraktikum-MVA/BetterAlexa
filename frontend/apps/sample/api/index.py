from flask import Flask, request
from gtts import gTTS
from waitress import serve
from langdetect import detect

import os
# import openai
import sys
import io
import urllib

from requests import post
from whisper import load_model
import numpy as np

# loading whisper model
WHISPER_MODEL = "tiny"
model = load_model(WHISPER_MODEL)

# stdout needs to be explicitly declared (only once) for docker logs
print("Configuring Flask", file=sys.stdout)
app = Flask(__name__)
app.logger.setLevel("INFO")


@app.route("/")
def home():
    return {"message": "Hello, World!"}


@app.route("/speech-to-text", methods=["POST"])
def process_audio():
    try:
        # Check if request method is POST
        if request.method != "POST":
            return "Method Not Allowed", 405

        # Parse incoming data as binary
        data = request.get_data()
        audioBlob = bytes(data)
        audioFile = io.BytesIO(audioBlob)
        audioFile.name = "audio.wav"  # Add a name attribute to the BytesIO object
        # transcript = openai.Audio.transcribe("whisper-1", audioFile)

        with open(audioFile.name, "wb") as audio_file:
            audio_file.write(audioBlob)

        transcription_result = model.transcribe(audioFile.name)

        os.remove(audioFile.name)

        # Here, you can process the audio data as needed. For example, you can
        # use a third-party library like `ffmpeg` to convert the audio to a
        # different format, analyze the audio data, etc.

        # Respond with success message
        return {"result": transcription_result}, 200
    except Exception as e:
        app.logger.error(f"Speech to text error: {e}")
        return {"error": "Internal Server Error"}, 500


@app.route("/command-to-action", methods=["POST"])
def generate_cta():
    try:
        # Check if request method is POST
        if request.method != "POST":
            return "Method Not Allowed", 405

        # Parse incoming data as binary
        data = request.get_data()
        spotify_token = request.headers.get("x-spotify-access-token", "undefined")
        text = data.decode("utf-8")

        # response = post("http://108.181.203.191:8047/t2c/{}".format(urllib.parse.quote(text, safe="/")))
        # response = post("http://108.181.203.191:8047/t2c/", json={"user_input": text})
        response = post("http://108.181.203.191:8007/t2c", json={"user_input": text}, headers={"x-spotify-access-token": spotify_token})

        json = response.json()

        result = {
            "text": json["message"],
            "qdrant": json["qdrant"]
            }
        # response = openai.ChatCompletion.create(
        #     model="gpt-3.5-turbo",
        #     messages=[
        #         {"role": "user", "content": f"{text}"},
        #     ],
        # )
        # result = {
        #     "text": response["choices"][0]["message"]["content"],
        # }

        # Respond with success message
        return {"result": result}, 200
    except Exception as e:
        app.logger.error(f"Command to action error: {e}")
        return {"error": f"Internal Server Error {e}"}, 500


@app.route("/text-to-speech", methods=["POST"])
def process_text():
    try:
        # Check if request method is POST
        if request.method != "POST":
            return "Method Not Allowed", 405

        # Parse incoming data as binary
        data = request.get_data()
        text = data.decode("utf-8")
        tts = gTTS(text=text, lang=detect(text))

        # return tts audio stream
        return tts.stream()
    except Exception as e:
        app.logger.error(f"Text to speech error: {e}")
        return {"error": "Internal Server Error"}, 500


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "dev":
        app.run(host="::", port=3001, debug=True)
    else:
        app.logger.info(" * Running production server on port 3001")
        serve(app, host="0.0.0.0", port=3001)
