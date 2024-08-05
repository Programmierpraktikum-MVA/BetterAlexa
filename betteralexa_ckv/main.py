import os
from eff_word_net.streams import SimpleMicStream
from eff_word_net.engine import HotwordDetector

from eff_word_net.audio_processing import Resnet50_Arc_loss

from eff_word_net import samples_loc

# from eff_word_net import RATE

from remote_whisper import get_path, play_audio, remote_whisper
 
# import sounddevice as sd

from vad import start_recording, save_audio

base_model = Resnet50_Arc_loss()

# Initialize the hotword detector
mycroft_hw = HotwordDetector(
    hotword="mycroft",
    model = base_model,
    reference_file=os.path.join(samples_loc, "alexa_ref.json"),
    threshold=0.7,
    relaxation_time=2
)

# Initialize the microphone stream
mic_stream = SimpleMicStream(
    window_length_secs=1.5,
    sliding_window_secs=0.75,
)

mic_stream.start_stream()

i = 0 # Counter for the input files
print("Starting script... Say Alexa to start.")
try:
    while True:
        # Get the frame and detect the hotword
        frame = mic_stream.getFrame()
        result = mycroft_hw.scoreFrame(frame)
        if result==None :
            # No voice activity, continue to the next frame
            continue
        if(result["match"]):
            mic_stream.close_stream()
            # Hotword detected
            print("Wakeword uttered",result["confidence"])
            
            data = start_recording()

            wav_filename = f"recorded_audio_{i}.wav"
            wav_path = get_path("audio_files", wav_filename)
            save_audio(data, wav_path)
            print(f"Recorded audio saves as {wav_path}")

            i += 1
            
            output_path, language = remote_whisper(wav_path) # Send the recording to the server and get the response
            print(output_path)
            play_audio(output_path) # Play the response

            # Close and restart the stream
            mic_stream.start_stream()
except KeyboardInterrupt:
    print("You pressed Ctrl+C!")
    # signal.signal(signal.SIGINT, signal_handler)