import io

import numpy as np
import pyaudio
import torch
import torchaudio
from pydub import AudioSegment

torch.set_num_threads(1)
import threading

device = torch.device('cpu')

import ssl
ssl._create_default_https_context = ssl._create_unverified_context
model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad', 
                                       model='silero_vad', 
                                       force_reload=True)

def validate(model,
             inputs: torch.Tensor):
    with torch.no_grad():
        outs = model(inputs)
    return outs


def int2float(sound):
    abs_max = np.abs(sound).max()
    sound = sound.astype('float32')
    if abs_max > 0:
        sound *= 1/32768
    sound = sound.squeeze()  # depends on the use case
    return sound

def stop():
    input("Press Enter to stop the recording:")
    global continue_recording
    continue_recording = False

FORMAT = pyaudio.paInt16
CHANNELS = 1
SAMPLE_RATE=16000
CHUNK = int(SAMPLE_RATE / 10)

audio = pyaudio.PyAudio()
stream = audio.open(format=FORMAT,
               channels=CHANNELS,
               rate=SAMPLE_RATE,
               input=True,
               frames_per_buffer=CHUNK,
               input_device_index=5)

info = audio.get_host_api_info_by_index(0)
numdevices = info.get('deviceCount')

for i in range(0, numdevices):
    if (audio.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
        print("Input Device id ", i, " - ", audio.get_device_info_by_host_api_device_index(0, i).get('name'))

num_samples = 1536

data = []
voiced_confidences = []

global continue_recording
continue_recording = True

stop_listener = threading.Thread(target=stop)
stop_listener.start()
        
print('Start Speaking...')        
while continue_recording:
    
    audio_chunk = stream.read(num_samples)
    audio_int16 = np.frombuffer(audio_chunk, np.int16)
    audio_float32 = int2float(audio_int16)
    
    new_confidence = model(torch.from_numpy(audio_float32), 16000).item()
    print(new_confidence)