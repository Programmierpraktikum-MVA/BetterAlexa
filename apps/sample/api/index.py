from flask import Flask, request

import openai
import io
import os

app = Flask(__name__)


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
        transcript = openai.Audio.transcribe("whisper-1", audioFile)

        # Here, you can process the audio data as needed. For example, you can
        # use a third-party library like `ffmpeg` to convert the audio to a
        # different format, analyze the audio data, etc.

        # Respond with success message
        return {"result": transcript}, 200
    except Exception as e:
        print(e)
        return {"error": "Internal Server Error"}, 500


@app.route("/call-to-action", methods=["POST"])
def generate_cta():
    try:
        # Check if request method is POST
        if request.method != "POST":
            return "Method Not Allowed", 405

        # Parse incoming data as binary
        data = request.get_data()
        text = data.decode("utf-8")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": f"{text}"},
            ],
        )
        result = {
            "text": response["choices"][0]["message"]["content"],
        }

        # Respond with success message
        return {"result": result}, 200
    except Exception as e:
        print(e)
        return {"error": "Internal Server Error"}, 500


if __name__ == "__main__":
    app.run(host="::", port=3001, debug=os.environ.get("DEBUG", False))
