import json
import os

# get the functions/classes from group a,b,c
from llama3 import LLama3
from gtts import gTTS
from wolfram import ask_wolfram_question
from wikipedia import getWikiPageInfo
from spotify import play,set_volume_to,pause,next,prev,turn_on_shuffle,turn_off_shuffle,decrease_volume,increase_volume,play_song,play_album,play_artist,add_to_queue
from playsound import playsound

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
    tts = gTTS(text=text, lang='en')
    tts.save("response.mp3")
    #playsound("response.mp3")
    #os.remove("response.mp3")  # Delete after playing


if __name__ == "__main__":
    with open('functions.json', 'r') as file:
        functions = file.read()

    model = LLama3("Llama-3-8B-function-calling", functions, "https://drive.google.com/drive/folders/1Q-EV7D7pEeYl1On_d2JzxFEB67-KmEm3?usp=sharing")
    while True:
        user_input = input("User: ")
        output = model.generate(user_input)
        if output.startswith("<functioncall> "):
            output = process_function_call(model, output)
        print("Assistant: " + output)
        speak(output)