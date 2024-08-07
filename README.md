# Better Alexa Project

Welcome to the Better Alexa Project! This repository contains various components and microservices designed to work together to create an enhanced voice assistant experience. This document will guide you through setting up and understanding the different parts of this project.

## Table of Contents
1. Project Structure
2. Getting Started
3. Directory Overview
4. Contributing
5. License

## Project Structure

```sh
.
├── backend
│   ├── audio_stream_client
│   ├── client
│   ├── indexing
│   └── server
├── chess
├── frontend
└── file_structure.txt
```

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 14+
- Docker

## Directory Overview

### backend
Contains the main implementation for the project from 2024.

#### audio_stream_client
Contains the client-side code for streaming audio to the server.

- `main.py`, `vad.py`, `remote_whisper.py`: Main scripts for audio processing.
- `requirements.txt`, `setup.md`: Dependencies and setup instructions.

#### client
Client-side scripts for testing the backend, allowing access to the application through other means than a website.

- `audio_recorder.py`, `client.py`, `textToSpeechToFile.py`: Main client scripts.
- `requirementsClient.txt`, `docu.md`: Dependencies and documentation.

#### server
Backend server code and microservices.

- **function_calling**: Includes the LLM (Llama) and the actions it can perform.
- **tutor_ai**: Tools related to Tutor AI / BetterAlexa interface.
- `microservices.py`, `server.py`, `service.py`: Main server scripts.
- `requirementsServer.txt`: Server dependencies.

### chess
Chess game implementation with a backend (Flask) and frontend (React).

- **chessFlask**: Backend logic for the chess game.
- **chessReact**: Frontend components for the chess game.

### frontend
Contains the implementation from 2023, including the entire frontend of the application as well as parts of the backend that have been adjusted.

- **apps**: Contains multiple frontend applications `exp0` and `nextjs`. Also contains backend-related applications `sample` and `command-to-action`.
- `docker-compose.yml`, `docs`: Docker configuration and documentation.

### indexing
Scripts and tools for indexing data, primarily focused on video indexing.

- **DataSetup**: Scripts for setting up data.
- `fastapi_index.py`, `loadqdrant.py`: Indexing scripts.
- `VideoIndexing.md`: Documentation for video indexing.

### notebooks
Jupyter notebooks for model fine-tuning.

- `llama3-fine-tuning-fc.ipynb`: Notebook for fine-tuning Llama 3 model.
