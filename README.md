# server.py

This script is used for the server side of the application. It uses a whisper and llama3 model to transcribe incoming audio from the client and generates an answer using predefined functions in `functions.json`, which will be sent back to the client in text form.

## Setup

1. **Python Version**: We tested it with 3.10 but similar versions will probably work as well. You can check your Python version by running `python --version` in your terminal.

2. **Virtual Environment**: It is recommended to create a virtual environment for running this script. You can do this by running the following commands in your terminal:

    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```

    This creates a new virtual environment in a directory named `.venv` and activates it. Preferably do this in the main directory.

3. **Install Requirements**: Install the required Python packages. You can do this by running `pip install -r requirementsServer.txt` in the client directory.

4. **Run the Script**: Just run `python server.py` in the terminal.

## Usage

Now you can use the client to use the service provided by the server. Sometimes you will see some activity like the search for wikipedia pages. 

# client/client.py

This script is used for the client side of the application. It's recording audio and sending it to the server which responds with a text. We then use google text2speech to translate it back to sound.

## Setup

1. **Python Version**: We tested it with 3.10 but similar versions will probably work as well. You can check your Python version by running `python --version` in your terminal.

2. **Virtual Environment**: It is recommended to create a virtual environment for running this script. You can do this by running the following commands in your terminal:

    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```

    This creates a new virtual environment in a directory named `.venv` and activates it. Preferably do this in the client directory.

3. **Install Requirements**: Install the required Python packages. You can do this by running `pip install -r requirementsClient.txt` in the client directory.

4. **Run the Script**: Ensure that the server is already running with `python server.py`. Then you should be able to run `python client.py` in the terminal in the client directory.

## Usage

First select your desired audio device. After that type 'y' if you are ready to record some audio. Press str + C if you are done with recording.
