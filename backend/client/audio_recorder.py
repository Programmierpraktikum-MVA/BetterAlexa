import os
import logging
import wave
import struct
from pvrecorder import PvRecorder

class AudioRecorder:
    """
    A class for recording audio using PvRecorder.

    Attributes:
        device_index (int): Index of the audio device to use.
        frame_length (int): Length of each audio frame.
        sample_rate (int): Sample rate of the audio.
        channels (int): Number of audio channels.
        sample_width (int): Sample width of the audio.
        path (str): Path to save the recorded audio.
        recorder (PvRecorder): PvRecorder object for recording audio.
        audio (list): List to store recorded audio frames.
    """

    def __init__(self, device_index=-1, frame_length=512, sample_rate=16000, channels=1, sample_width=2, path='audio_recording.wav'):
        """
        Initializes the AudioRecorder with the given parameters.
        
        Args:
            device_index (int): Index of the audio device to use. Default is -1.
            frame_length (int): Length of each audio frame. Default is 512.
            sample_rate (int): Sample rate of the audio. Default is 16000.
            channels (int): Number of audio channels. Default is 1.
            sample_width (int): Sample width of the audio. Default is 2.
            path (str): Path to save the recorded audio. Default is 'audio_recording.wav'.
        """
        self.device_index = device_index
        self.frame_length = frame_length
        self.sample_rate = sample_rate
        self.channels = channels
        self.sample_width = sample_width
        self.path = path
        self.recorder = PvRecorder(device_index=self.device_index, frame_length=self.frame_length)
        self.audio = []

    @staticmethod
    def list_devices():
        """
        Prints the available audio devices.
        """
        devices = PvRecorder.get_available_devices()
        print("Available audio devices:")
        for index, device in enumerate(devices):
            print(f"[{index}] {device}")

    def start_recording(self):
        """
        Starts recording audio. Stops recording on KeyboardInterrupt and saves the recorded audio.
        """
        try:
            self.recorder.start()
            print("Recording... Press Ctrl+C to stop.")
            while True:
                frame = self.recorder.read()
                self.audio.extend(frame)
        except KeyboardInterrupt:
            print("Stopping recording...")
            self.stop_and_save_recording()
        except Exception as e:
            logging.error(f"An error occurred during recording: {e}")
            self.recorder.stop()

    def stop_and_save_recording(self):
        """
        Stops recording and saves the recorded audio to a file.
        """
        try:
            self.recorder.stop()
            with wave.open(self.path, 'w') as f:
                f.setparams((self.channels, self.sample_width, self.sample_rate, 0, 'NONE', 'not compressed'))
                audio_data = struct.pack('<' + ('h' * len(self.audio)), *self.audio)
                f.writeframes(audio_data)
            self.audio = []
            print(f"Recording saved to {self.path}")
        except Exception as e:
            logging.error(f"An error occurred while saving the recording: {e}")

    def delete_recorder(self):
        """
        Deletes the recorder object, freeing up resources.
        """
        self.recorder.delete()
        if os.path.isfile(self.path):
            os.remove(self.path)

# Example usage:
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    
    AudioRecorder.list_devices()
    device_index = int(input("Enter device index: "))
    recorder = AudioRecorder(device_index)
    try:
        recorder.start_recording()
    finally:
        recorder.delete_recorder()
        print("All done!")
