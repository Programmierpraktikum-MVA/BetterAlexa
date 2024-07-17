import os
from flask import Flask, request, jsonify, render_template
import speech_recognition as sr
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_audio():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file"}), 400

    audio_file = request.files['audio']

    recognizer = sr.Recognizer()
    
    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)
    
    try:
        text = recognizer.recognize_google(audio_data, language="de-DE")  # oder "en-US" für Englisch
        print(text)
        return jsonify({"transcription": text, "filename": audio_file.filename})
    except sr.UnknownValueError:
        return jsonify({"error": "Could not understand audio"}), 400
    except sr.RequestError:
        return jsonify({"error": "Could not request results from service"}), 500

if __name__ == '__main__':
    app.run(debug=True)