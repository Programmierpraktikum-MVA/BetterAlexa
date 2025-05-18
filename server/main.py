import pygame
import numpy as np
import io
import asyncio
from audio_interface import listen_for_voice
from s2t_nl import transcribe_response
from TTS.api import TTS
import soundfile as sf



# Initialize TTS model
tts = TTS(model_name="tts_models/en/vctk/vits", progress_bar=False)

sample_rate = tts.synthesizer.output_sample_rate

def play_audio(audio_array, sample_rate):
    """Convert NumPy array to WAV in memory and play it using pygame."""
    buffer = io.BytesIO()
    sf.write(buffer, audio_array, samplerate=sample_rate, format="WAV")
    buffer.seek(0)

    pygame.mixer.init(frequency=sample_rate)
    pygame.mixer.music.load(buffer)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    pygame.mixer.quit()

async def main():
    
    while True:
        audio_np = listen_for_voice()

        if audio_np is None or len(audio_np) == 0:
            continue

        try:
            text = await transcribe_response(audio_np)
            print("> Transcribed text:", text)
        except Exception as e:
            print(f"[ERROR] Transcription failed: {e}")
            continue
	 # you can change the speaker using a different id
            # p234,p273,p330,p335,p34,p227,...and there are more
        try:
            audio_array = tts.tts(text=text, speaker="p335")
            play_audio(audio_array, sample_rate)
        except Exception as e:
            print(f" > TTS playback failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
