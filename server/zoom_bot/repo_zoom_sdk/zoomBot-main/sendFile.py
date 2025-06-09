import os
import logging
import pygame
from gtts import gTTS
from requests import post
from os import path
from audio_recorder import AudioRecorder
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

SERVER_URL = "http://127.0.0.1:8006/whisper"

def get_path(file_name):
    """
    Constructs the full path for the given file name.
    
    Args:
        file_name (str): The name of the file.

    Returns:
        str: The full file path.
    """
    return path.join(path.dirname(path.abspath(__file__)), file_name)

def remote_whisper(input_file_path):
    """
    Sends the local audio file to the server and returns the response text.
    
    Args:
        input_file_path (str): The path to the input audio file.

    Returns:
        tuple: The server response text or status code, and an error number.
    """
    try:
        with open(input_file_path, "rb") as file:
            files = {"file": file}
            response = post(SERVER_URL, files=files)
        if response.status_code == 200:
            print("all good")
            return response.text, 0
        else:
            print("server error")
            return response.status_code, -1
    except Exception as e:
        print("exception")
        print(e)
        return e, -2
    


def main():
    print(sys.argv[1])
    response, errno = remote_whisper(sys.argv[1])
    script_dir = os.path.dirname(os.path.abspath(__file__))

    if errno == 0:
        print(errno)
        print()
        filename = os.path.join(script_dir, "response.mp3")
        # text2speech from google
        tts = gTTS(text=response, lang='en')
        tts.save(filename)
    else:
        filename = os.path.join(script_dir, "error")
        f = open(filename,"w")
        f.write(str(response))
        f.close()
    f = open(os.path.join(script_dir,"done"),"w")
    f.write(".")
    f.close()
    
if __name__ == "__main__":
    main()
