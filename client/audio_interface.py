import webrtcvad
import numpy as np
import collections
from pvrecorder import PvRecorder
#import wave
SAMPLE_RATE = 16000
FRAME_DURATION = 30
FRAME_SIZE = int(SAMPLE_RATE * FRAME_DURATION / 1000)
CHANNELS = 1

vad = webrtcvad.Vad(2)

def get_audio_stream():
    recorder = PvRecorder(device_index=-1, frame_length=FRAME_SIZE)
    return recorder

def listen_for_voice():
    recorder = get_audio_stream()
    ring_buffer = collections.deque(maxlen=10)
    voiced_frames = []
    triggered = False
    silence_counter = 0

    recorder.start()
    print(" > Listening...")

    try:
        while True:
            frame = recorder.read()
            frame_bytes = np.array(frame, dtype=np.int16).tobytes()
            is_speech = vad.is_speech(frame_bytes, SAMPLE_RATE)

            if not triggered:
                ring_buffer.append((frame_bytes, is_speech))
                if sum(1 for _, s in ring_buffer if s) > 0.8 * len(ring_buffer):
                    triggered = True
                    voiced_frames.extend(f for f, _ in ring_buffer)
                    ring_buffer.clear()
            else:
                voiced_frames.append(frame_bytes)
                if not is_speech:
                    silence_counter += 1
                    if silence_counter > 30:
                        break
                else:
                    silence_counter = 0
    finally:
        print(" > Stopped listening.")
        recorder.stop()
        recorder.delete()

    audio_bytes = b''.join(voiced_frames)
    audio_np = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
    return audio_np


#FOR TESTING


def save_audio_to_wav(audio_np, filename="output.wav"):

    if audio_np is None or len(audio_np) == 0:
        print("[WARNING] No audio data to save.")
        return

    # Convert back to int16 for WAV saving
    audio_int16 = np.clip(audio_np * 32768, -32768, 32767).astype(np.int16)

    with wave.open(filename, 'w') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)  # 2 bytes for int16
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(audio_int16.tobytes())

    print(f"[INFO] Audio saved to {filename}")


# Example usage
if __name__ == "__main__":
    audio = listen_for_voice()
    save_audio_to_wav(audio, "vad_voice_output.wav")
