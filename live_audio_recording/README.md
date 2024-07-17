## Description
This directory contains a demo for a website that continuously records audio and sends it to flask endpoint (/upload). In this example, the audio is transcribed to text and output to the console.
But of course you can use the audio files for other things.

## Usage

1. **Virtual Environment (Optional)** Create a virtual environment via virtualenv venv and activate it:
    
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```
2. **Install Requirements** Install the required python packages. You can use the command `pip install -r requirements.txt`
3. **Run the demo** Simply run `python app.py` in the terminal
4. **Enjoy** Now you should be able to open the website (usually 127.0.0.1:5000) and record audio!