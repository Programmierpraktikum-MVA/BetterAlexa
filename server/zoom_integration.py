import sounddevice as sd
import numpy as np

def get_headset_sound():
    """
    records for a given duration all output from the Zoom Session via Loopback
    which should be the default device for Zoom

    duration, samplerate and channels can be configured depending on the 
    Zoom/ ALSA config
    """
    duration = 5 # how long do we want to record
    samplerate = 48000 # maybe it is 44100 look into zoom/alsa config
    channels = 2

    output_device = 'hw:Loopback,1,0'

    print("Recording Zoom output...")
    # audio is the array that can be feed to the ai
    audio_output_stream = sd.rec(int(duration*samplerate), samplerate=samplerate, channels=channels, dtype='float32', device=output_device) 
    sd.wait()
    print("Done recording")


def play_mic_sound(audio_input_stream):
    """
    gets an NumPy array that should be played in the Zoom Session
    and plays it over Loopback which should be the default device for Zoom

    duration, samplerate and channels can be configured depending on the 
    Zoom/ ALSA config
    """
    duration = 5 # how long do we want to record
    samplerate = 48000 # maybe it is 44100 look into zoom/alsa config
    channels = 2

    input_device = 'hw:Loopback,0,0'
    print("Playing audio into Zoom input...")
    sd.play(audio_input_stream, samplerate=samplerate, device=input_device)
    sd.wait()
    print("Done.")

