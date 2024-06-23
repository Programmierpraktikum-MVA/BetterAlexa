import os
import uuid
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
client = ElevenLabs(
    api_key=ELEVENLABS_API_KEY,
)


def text_to_speech_file(text: str, language: str, gender: str) -> str:
    # Calling the text_to_speech conversion API with detailed parameters
    voiceId = "pNInz6obpgDQGcFmaJgB"
    if gender == "female":
        voiceId = "EXAVITQu4vr4xnSDxMaL"
    modelId = "eleven_turbo_v2"
    if language == "german":
        #voiceId = 'eWzPDynr2HAv14m40xnj'
        #voiceId = "Julius Deutsch"
        modelId = "eleven_multilingual_v2"
    response = client.text_to_speech.convert(
        voice_id=voiceId, 
        optimize_streaming_latency="0",
        output_format="mp3_22050_32",
        text=text,
        model_id=modelId, # use the turbo model for low latency, for other languages use the `eleven_multilingual_v2`
        voice_settings=VoiceSettings(
            stability=0.9, #0.0 emotional to 1.0 very neutral
            similarity_boost=1.0,
            style=0.0,
            use_speaker_boost=True,
        ),
    )

    # uncomment the line below to play the audio back
    # play(response)

    # Generating a unique file name for the output MP3 file
    save_file_path = "output.mp3"

    # Writing the audio to a file
    with open(save_file_path, "wb") as f:
        for chunk in response:
            if chunk:
                f.write(chunk)

    #print(f"{save_file_path}: A new audio file was saved successfully!")

    # Return the path of the saved audio file
    return save_file_path

if __name__ == "__main__":
    text_to_speech_file("Hello I am Alex", "english", "male")
