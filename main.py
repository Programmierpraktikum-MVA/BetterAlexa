import json

# get the functions/classes from group b,c
from llama3 import LLama3
from wolfram import ask_wolfram_question
from wikipedia import getWikiPageInfo
from spotify import play,set_volume_to,pause,next,prev,turn_on_shuffle,turn_off_shuffle,decrease_volume,increase_volume,play_song,play_album,play_artist,add_to_queue
from textToSpeechToFile import text_to_speech_file
from tutor_ai.backend.ChatEngine import ask_TutorAI_question

DEBUG_MODE = 1

def process_function_call(model : LLama3, fc: str) -> str:
    if DEBUG_MODE:
        print(fc)
    fc = fc[len("<functioncall> "):]
    fc = fc.replace("'", "")
    try: 
        data = json.loads(fc)
    except:
        result = 'FUNCTION RESPONSE: Invalid input format, try again' 
        if DEBUG_MODE:
            print(result)
        return model.generate(result)
    name = data["name"]
    arguments = data["arguments"]
    result = globals()[name](**arguments)
    result = {"result": result}
    result = 'FUNCTION RESPONSE: ' + str(result)
    if DEBUG_MODE:
        print(result)
    return model.generate(result)

def process_input(model: LLama3, transcription: str):
    output = model.generate(transcription)
    if output.startswith("<functioncall> "):
        output = process_function_call(model, output)
    return output

if __name__ == "__main__":
    with open('functions.json', 'r') as file:
        functions = file.read()
    llamaModel = LLama3("Llama-3-8B-function-calling", functions, "https://drive.google.com/drive/folders/1CJtn-3nCfQT3FU3pOgA3zTIdPLQ9n3x6?usp=sharing", "https://drive.google.com/drive/folders/1RmhIu2FXqwu4TxIQ9GpDtYb_IXWoVd7z?usp=sharing")
    while True:
        user_input = input("User: ")
        output = process_input(llamaModel, user_input)
        print("Assistant: " + output)