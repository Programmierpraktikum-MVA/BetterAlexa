import os
import logging
import pygame
from gtts import gTTS
from requests import post
from os import path
from audio_recorder import AudioRecorder

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

SERVER_URL = "http://108.181.203.191:8006/whisper"


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
            return response.text, 0
        else:
            return response.status_code, -1
    except Exception as e:
        return e, -2
    
def play_sound(text: str):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(script_dir, "response.mp3")
    # text2speech from google
    tts = gTTS(text=text, lang='en')
    tts.save(filename)
    # play sound using pygame
    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()
    try:
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
    except KeyboardInterrupt:
        pass
    finally:
        pygame.mixer.music.stop()
        pygame.mixer.quit()

def main():
    """
    Main function that handles the audio recording and communication with the server.

    This function lists the available audio devices, prompts the user to select a device,
    initializes the audio recorder, and enters a loop to record audio and send it to the server.
    The user can choose to record more audio or exit the loop.
    """
    # List available audio devices
    AudioRecorder.list_devices()
    device_index = int(input("Enter device index: "))
    
    # Initialize the audio recorder
    recorder = AudioRecorder(device_index)
    
    while True:
        record_audio = input("Would you like to record some audio (y/n)?: ")
        if record_audio.lower() == "y":
            recorder.start_recording()

            # Send the recorded audio to the server
            print("Recording finished and saved. Sending to server...")
            response, errno = remote_whisper(recorder.path)
            
            # Handle the server response
            if errno == 0:
                print(f"Response: {response}\n")
                play_sound(response)
            elif errno == -1:
                logging.error(f"Server responded with status code: {response}")
            elif errno == -2:
                logging.error(f"Error contacting server: {response}")
            else:
                logging.error(f"Unknown error {errno}: {response}")

        elif record_audio.lower() == "n":
            break
        else:
            print(f"Invalid input '{record_audio}'. Use 'y' for yes and 'n' for no. Try again.")
    
    print("All done!")
    recorder.delete_recorder()

if __name__ == "__main__":
    main()
