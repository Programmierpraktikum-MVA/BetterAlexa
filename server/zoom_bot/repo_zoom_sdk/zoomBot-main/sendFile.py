import os
import logging
#import pygame
#from gtts import gTTS
from requests import post
import httpx
from os import path
#from audio_recorder import AudioRecorder
import sys
import soundfile as sf

import numpy
import asyncio
import re
#from meeting_sdk import get_user_id

# TODO: check if requirements need to be updated

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

SERVER_URL = "http://127.0.0.1:8000/api/v1/stream"

def get_path(file_name):
    """
    Constructs the full path for the given file name.
    
    Args:
        file_name (str): The name of the file.

    Returns:
        str: The full file path.
    """
    return path.join(path.dirname(path.abspath(__file__)), file_name)

"""
def remote_whisper(input_file_path):
    """
"""
    Sends the local audio file to the server and returns the response text.
    
    Args:
        input_file_path (str): The path to the input audio file.

    Returns:
        tuple: The server response text or status code, and an error number.
    """
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
"""

def wav_to_np_array(file_path, normalized=False):
    pcm, sample_rate = sf.read(file_path, always_2d=False)   # pcm is float32/-64
    if not normalized and pcm.dtype.kind == "f":              # convert to int16 if caller expects raw
        pcm = (pcm * 32768).astype("int16")
    return sample_rate, pcm  

async def save_stream_to_file(streamer, filename):
    """
    Save the given streamer object one chunk at a time to a new file at the location of filename.

    Args:
        streamer: continuous audio_stream divided into chunks.
        filename (str): name of the file where the stream should be saved. 

    """
    with open(filename, "wb") as f:
        async for chunk in streamer:
            f.write(chunk)

async def main():
    """
    Sends the local audio file to the server and returns the response audiostream.
    This response is saved into a file and will be accessed for playback into zoom.
    
    Args:
        sys.argv[1] is a filepath to the local audio file and the programm needs to be executed with this. 

    Returns:
        local audiostream response.wav is written with the response of the server.
    """
    # get the user_id from the meeting_sdk.cpp file via pybind11
    #user_id = get_user_id()
    #print("User ID from C++:", user_id)

    # workaround for meeting id instead of user_id
    config_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.txt")
    with open(config_file_path, "r") as f:
        lines = f.readlines()
    
    meeting_id_str = lines[0]
    match = re.search(r'"([^"]+)"', meeting_id_str)
    meeting_id = 0
    if match:
        meeting_id = match.group(1)

    print(f"Sending following file: {sys.argv[1]}")
    print(f"The send meeting id is {meeting_id}")
    sample_rate, pcm = wav_to_np_array(sys.argv[1], normalized=True)

    payload = {
        "meeting_id": meeting_id,
        "pcm": pcm.tolist(),                     # JSON-friendly
    }

    script_dir = os.path.dirname(os.path.abspath(__file__)) 

    try:
        async with httpx.AsyncClient() as client:
            async with client.stream("POST", SERVER_URL, json=payload) as resp:
                resp.raise_for_status()
                out_path = os.path.join(script_dir, "response.wav")  
                with open(out_path, "wb") as f:
                    async for chunk in resp.aiter_bytes():
                        f.write(chunk)
    except Exception as e:
        logging.debug(f"Error, trying to get response from Server: {e}")
        with open(os.path.join(script_dir, "error"), "w") as f:
            f.write(str(e))

    
"""   (old version)
    # send the audiostream to the server and wait for a response
    try:    
        response = await post(SERVER_URL, json=payload)
        response.raise_for_status()
    except Exception as e:
        # write errors that are raised into an error file
        logging.debug(f"Error, trying to get response from Server: {e}") 
        with open(os.path.join(script_dir, "error"),"w") as f:
            f.write(str(response))

    
    print(f"← {len(response.content)/1024:.1f} KB audio from server – received")
    wav_bytes = response.content    
    
    # save the response audiostream into the response file  
    filename =  os.path.join(script_dir, "response.wav")
    await save_stream_to_file(wav_bytes, filename)

    # write a done marker into a separat file
    with open(os.path.join(script_dir, "done"), "w") as f:
        f.write(".")
"""    

""" old version (not needed anymore)
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
    """
if __name__ == "__main__":
    asyncio.run(main())
