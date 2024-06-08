import json
import os

# get the functions/classes from group a,b,c
from llama3 import LLama3
from gtts import gTTS
from wolfram import ask_wolfram_question
from wikipedia import getWikiPageInfo
from spotify import play,set_volume_to,pause,next,prev,turn_on_shuffle,turn_off_shuffle,decrease_volume,increase_volume,play_song,play_album,play_artist,add_to_queue
from playsound import playsound
from textToSpeechToFile import text_to_speech_file

DEBUG_MODE = 0

def process_function_call(model : LLama3, fc: str) -> str:
    if DEBUG_MODE:
        print(fc)
    fc = fc[len("<functioncall> "):]
    fc = fc.replace("'", "")
    data = json.loads(fc)
    name = data["name"]
    arguments = data["arguments"]
    result = globals()[name](**arguments)
    result = {"result": result}
    result = 'FUNCTION RESPONSE: ' + str(result)
    if DEBUG_MODE:
        print(result)
    return model.generate(result)

def speak(text: str):
    text_to_speech_file(text, "english", "female")
    #playsound("output.mp3")
    #os.remove("output.mp3")  # Delete after playing

def process_input(transcription: str):
    with open('functions.json', 'r') as file:
        functions = file.read()
    model = LLama3("Llama-3-8B-function-calling", functions, "https://drive.google.com/drive/folders/1Q-EV7D7pEeYl1On_d2JzxFEB67-KmEm3?usp=sharing")
    output = model.generate(transcription)
    if output.startswith("<functioncall> "):
        output = process_function_call(model, output)
    return output

if __name__ == "__main__":
    while True:
        user_input = input("User: ")
        output = process_input(user_input)
        print("Assistant: " + output)
        speak(output)