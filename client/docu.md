# Audio Recorder and Client-Server Communication Documentation

## Overview

This project consists of two main components:
1. **Audio Recorder (`audio_recorder.py`)**: A class-based implementation to record audio using `PvRecorder`.
2. **Client (`client.py`)**: A client script that records audio using the `AudioRecorder` class and sends the recorded audio to a server for processing.

## Components

### Audio Recorder (`audio_recorder.py`)

This script defines the `AudioRecorder` class which is responsible for:
- Listing available audio devices.
- Recording audio from a specified device.
- Stopping the recording and saving the audio to a file.
- Deleting the recorder object to free up resources.

#### Attributes
- `device_index (int)`: Index of the audio device to use. Default is -1.
- `frame_length (int)`: Length of each audio frame. Default is 512.
- `sample_rate (int)`: Sample rate of the audio. Default is 16000.
- `channels (int)`: Number of audio channels. Default is 1.
- `sample_width (int)`: Sample width of the audio. Default is 2.
- `path (str)`: Path to save the recorded audio. Default is 'audio_recording.wav'.
- `recorder (PvRecorder)`: PvRecorder object for recording audio.
- `audio (list)`: List to store recorded audio frames.

#### Methods
- `list_devices()`: Prints the available audio devices.
- `start_recording()`: Starts recording audio. Stops recording on KeyboardInterrupt and saves the recorded audio.
- `stop_and_save_recording()`: Stops recording and saves the recorded audio to a file.
- `delete_recorder()`: Deletes the recorder object, freeing up resources.

#### Example Usage
```python
AudioRecorder.list_devices()
device_index = int(input("Enter device index: "))
recorder = AudioRecorder(device_index)
try:
    recorder.start_recording()
finally:
    recorder.delete_recorder()
    print("All done!")
```

### Client (`client.py`)
This script handles the client-side functionality, including:
- Listing available audio devices.
- Recording audio using the `AudioRecorder` class.
- Sending the recorded audio to a server for processing.
- Handling the server response and errors.

#### Functions

- `get_path(file_name)`: Constructs the full path for the given file name.
    - **Args**: `file_name (str)`: The name of the file.
    - **Returns**: `str`: The full file path.

- `remote_whisper(input_file_path)`: Sends the local audio file to the server and returns the response text.
    - **Args**: `input_file_path (str)`: The path to the input audio file.
    - **Returns**: `tuple`: The server response text or status code, and an error number.

- `main()`: The main function that handles the audio recording and communication with the server.

#### Server URL

- `SERVER_URL`: The URL of the server to which the audio file is sent. Default is `"http://0.0.0.0:8006/whisper"`.

#### Example Usage
```python
if __name__ == "__main__":
    main()
```

## How to Use

1. **Set Up Environment**: Ensure you have the necessary environment and dependencies set up. This includes installing `PvRecorder` and `requests` library. Installation can be done using the `requirements.txt` file.
```bash
python -m pip install -r requirements.txt
```

2. **Run Audio Recorder**: Execute the `audio_recorder.py` script to list available audio devices and record audio.
```bash
python audio_recorder.py
```

3. **Run Clien**: Execute the `client.py` script to record audio and send it to the server.
```bash
python client.py
```

4. **Interaction**:
- The script will prompt you to select an audio device by entering its index.
- You can then start recording audio by pressing 'y' when prompted.
- To stop recording, press `Ctrl+C`.
- The recorded audio will be sent to the server, and the response will be printed.

## Server Endpoint
- **URL**: `http://0.0.0.0:8006/whisper`
- **Method**: `POST`
- **Input**: Audio file (`.wav` format).
- **Output**: Transcription text or an error message.

## Important Notes
- Ensure the server is running and accessible at the specified `SERVER_URL`.
- Handle exceptions and errors gracefully to prevent crashes and data loss.
- Keep the audio recording duration reasonable to avoid large file sizes and long processing times.

## Dependencies
- `os`
- `PvRecorder`
- `requests`
- `wave`
- `struct`
- `logging`
