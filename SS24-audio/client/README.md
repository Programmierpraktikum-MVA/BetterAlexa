# main.py

This script is used to record audio, send it to a server for processing, and play the response.

## Setup

1. **Python Version**: Ensure you have Python version between 3.6 and 3.9 installed on your system. You can check your Python version by running `python --version` in your terminal.

2. **Virtual Environment**: It is recommended to create a virtual environment for running this script. You can do this by running the following commands in your terminal:

    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```

    This creates a new virtual environment in a directory named `.venv` and activates it. Preferably do this in the client directory.

3. **Install Requirements**: Install the required Python packages. You can do this by running `pip install -r requirements.txt` in the client directory. During installation, you may encounter an error about `efficientword`. You can ignore this error for now.

4. **Run the Script**: Try running the script by typing `python test.py` in your terminal. If the script runs successfully despite the `efficientword` error, you can proceed to the next step.

5. **Server Setup**: Ensure that the server is running. This script sends audio data to a server for processing, so the server needs to be running for the script to work. See the server README for more information on setting up the server.

## Usage

After setting up, wait for the message "Starting script... say Alexa to start." Once you see this message, you can start using the script. Say "Alexa" to start recording audio. The recorded audio will be sent to the server for processing, and the response will be played back.

