from audio_interface import listen_for_voice
from s2t_nl import transcribe_response
from TTS.api import TTS
import sounddevice as sd
import asyncio

sample_rate = 22050  # Common sample rate for TTS models
tts = TTS(model_name="tts_models/en/vctk/vits", progress_bar=False)

async def main():
    # show available input/output audio devices
    print(sd.query_devices())
    while True:
        audio_np = listen_for_voice()

        if audio_np is None or len(audio_np) == 0:
            # print("no audio")
            continue

        try:
            text = await transcribe_response(audio_np)
            print("Transcribed text:", text)
        except Exception as e:
            print(f" Transcription failed: {e}")
            continue

        try:
            # you can change the speaker using a different id
            # p234,p273,p330,p335,p34,p227,...and there are more
            audio_array = tts.tts(text=text, speaker="p335")
            sd.play(audio_array, samplerate=sample_rate)
            sd.wait()
        except Exception as e:
            print(f" TTS playback failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
