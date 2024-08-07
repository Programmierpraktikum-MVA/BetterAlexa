import wave
import time
import numpy as np
import torch
torch.set_num_threads(1)
import torchaudio
torchaudio.set_audio_backend("soundfile")
import pyaudio

import ssl
ssl._create_default_https_context = ssl._create_unverified_context
model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad',
                              model='silero_vad',
                              force_reload=True)

(get_speech_timestamps,
 save_audio,
 read_audio,
 VADIterator,
 collect_chunks) = utils

# Taken from utils_vad.py
def validate(model,
             inputs: torch.Tensor):
    with torch.no_grad():
        outs = model(inputs)
    return outs

# Provided by Alexander Veysov
def int2float(sound):
    abs_max = np.abs(sound).max()
    sound = sound.astype('float32')
    if abs_max > 0:
        sound *= 1/32768
    sound = sound.squeeze()  # depends on the use case
    return sound

FORMAT = pyaudio.paInt16
CHANNELS = 1
SAMPLE_RATE = 16000
CHUNK = int(SAMPLE_RATE / 10)

audio = pyaudio.PyAudio()

info = audio.get_host_api_info_by_index(0)
numdevices = info.get('deviceCount')

for i in range(0, numdevices):
    if (audio.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
        print("Input Device id ", i, " - ", audio.get_device_info_by_host_api_device_index(0, i).get('name'))

device_index = int(input("Enter desired device's index: "))

num_samples = 1536

def open_stream():
    stream = audio.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=SAMPLE_RATE,
                        input=True,
                        frames_per_buffer=CHUNK,
                        input_device_index=device_index)
    return stream

def save_audio(data, filename):
    wf = wave.open(filename, "wb")
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(SAMPLE_RATE)
    wf.writeframes(b"".join(data))
    wf.close()

def start_recording(min_time=5, max_silence=2):
    data = []
    start_time = time.time()
    last_speech = start_time

    stream = open_stream()
    print("Started recording")
    while True:
        if time.time() - start_time > min_time and time.time() - last_speech > max_silence:
            break

        audio_chunk = stream.read(num_samples, exception_on_overflow=False)

    
        # in case you want to save the audio later
        data.append(audio_chunk)
        
        audio_int16 = np.frombuffer(audio_chunk, np.int16);

        audio_float32 = int2float(audio_int16)
        
        # get the confidences and add them to the list to plot them later
        new_confidence = model(torch.from_numpy(audio_float32), 16000).item()
        # print("speech confidence:", new_confidence)
        if new_confidence > 0.7:
            last_speech = time.time()

    stream.stop_stream()
    stream.close()

    print("Stopped the recording")
    return data