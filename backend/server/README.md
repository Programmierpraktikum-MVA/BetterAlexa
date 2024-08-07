# Backend Server Directory

This directory contains the backend server code and microservices for the Better Alexa Project. The main components include the function_calling module, microservices, and various utilities to support the server functionality.

## Directory Overview

### function_calling
Contains everything related to the Llama model and the actions it can perform.

- **actions**: Scripts for handling various actions such as Spotify, Wikipedia, WolframAlpha queries, and database handling.
  - `database_handling.py`, `spotify.py`, `spotify_utils.py`, `wikipedia.py`, `wolfram.py`
- `download_drive.py`: Script for downloading drive data (model parameters).
- `fastapi_llama3.py`: Main script to start the FastAPI server for Llama model.
- `functions.json`: JSON file defining the functions.
- `llama3.py`: Script for Llama model operations.
- `main.py`: Main script for running the function_calling module.
- `requirementsServer.txt`: Dependencies for the server.
- **tutor_ai**: Contains tools related to the Tutor AI / BetterAlexa interface.

### microservices
Contains TTS and STT microservices that can run separately or be incorporated into the frontend code.

- `Dockerfile`: Docker configuration for the microservices.
- `microservices.py`: Main script for microservices.

### notebooks
Contains Jupyter notebooks for data analysis and model fine-tuning.

- `llama3-fine-tuning-fc.ipynb`: Notebook for fine-tuning the Llama3 model.

### Other files
- `requirementsServer.txt`: Server dependencies.
- `server.py`: Server wrapper script for service.py.
- `service.py`: Main server functionality with TTS, STT and Llama.

## Getting Started

### Prerequisites

- Python 3.8+
- Docker

### Installation

1. **Create and activate a virtual environment**

   ```sh
   cd function_calling
   python -m venv .venv
   source .venv/bin/activate
   ```

2. **Install dependencies**

   ```sh
   pip install -r requirementsServer.txt
   ```

### Running the FastAPI Server

To start the FastAPI server for the Llama model, navigate to the `function_calling` directory and run the `fastapi_llama3.py` script.

1. **Navigate to the function_calling directory**

   ```sh
   cd function_calling
   ```

2. **Run the FastAPI server**

   ```sh
   uvicorn --host 0.0.0.0 --port 8007 fastapi_llama3:app
   ```

The server should now be running, and you can access the Llama model's functionality through the defined endpoints.
