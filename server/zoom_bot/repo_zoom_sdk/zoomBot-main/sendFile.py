import os
import logging
#import pygame
#from gtts import gTTS
from requests import post
from os import path
#from audio_recorder import AudioRecorder
import sys
from pydub import AudioSegment
import numpy
import asyncio
#import meeting_sdk

# TODO: check if requirements need to be updated

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

SERVER_URL = "http://127.0.0.1:8006/api/v1/stream"

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

def mp3_to_np_array(file_path, normalized=False):
    """
    Converts a mp3_file located at file_path to a (normalized) np_array. 
    
    Args:
        file_path (str): The path to the input audio file (mp3).
        normalized (bool): Set true if we want to normalize the output array.

    Returns:
        audio.frame_rate:   The sample rate of the mp3 file.
        array:              The (normalized) np_array containing the audio.
    """
    audio = AudioSegment.from_mp3(file_path)
    array = numpy.array(audio.get_array_of_samples())
    # Handle stereo files
    if audio.channels == 2:
        array = array.reshape((-1, 2))
    if normalized:
        return audio.frame_rate, numpy.float32(array) / 2**15
    else:
        return audio.frame_rate, array    

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
    #user_id = meeting_sdk.get_user_id()
    user_id = 1
    print("User ID from C++:", user_id)

    print(f"Sending following file: {sys.argv[1]}")
    sample_rate, pcm = mp3_to_np_array(sys.argv[1])
    payload = {
        "meeting_id": str(user_id),
        "pcm": pcm.tolist(),                     # JSON-friendly
    }

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
    script_dir = os.path.dirname(os.path.abspath(__file__))   
    filename =  os.path.join(script_dir, "response.wav")
    await save_stream_to_file(wav_bytes, filename)

    # write a done marker into a separat file
    with open(os.path.join(script_dir, "done"), "w") as f:
        f.write(".")
    

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
