# BetterAlexa

Welcome to **BetterAlexa** — a speech- and text-driven personal assistant that listens, thinks, and acts. It consists of a Python server for talking/tool-calling, a simple Python voice client, a web interface and an Integration with Discord (Text) and Zoom (Speech). The website depends on the server being up.

---

## What’s in this repository?

```
.
├─ server/          # Python backend (Whisper, Llama 3 reasoning, tool/function calls, database)
├─ client/          # Python voice client (records audio, sends to server, plays TTS)
├─ web_interface/   # Web UI that interacts with the DB
├─ .gitattributes
├─ .gitignore
├─ README.md
└─ test_tutorai.py
```

> Notes
> - The backend transcribes audio with Whisper and uses an LLM (Llama 3) plus predefined functions (see `functions.json`) to generate responses.
> - The **website requires the server** to be running and reachable.

---

## Prerequisites

- **Python**: 3.10 (project was tested with 3.10)
- ~30gb of local storage for LLM and libraries 

---

## Setup — Server (required)

The server handles audio transcription, reasoning, and tool calls.

1. **Create and activate a virtual environment** (from the repo root):
   ```bash
   python -m venv .venv
   # macOS/Linux
   source .venv/bin/activate
   # Windows (PowerShell)
   .venv\Scripts\Activate.ps1
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirementsServer.txt
   ```

3. **(Optional) Configure integrations**  
   If you plan to use API-based integrations (e.g., Discord), create a `.env` file with your tokens/secrets. Do **not** commit this file.

4. **Run the server**:
   ```bash
   python server.py
   ```
   The server will run on local interfaces by default. This can be changed by adding the flags --tcp, --port 8000, --host 0.0.0.0
> Keep this terminal running. The **web interface** depends on this server.
> If you want to use the discord but, you have to start it seperately (see /server/discord_bot.py)
---

## Setup — Python Voice Client (depends on the server)

1. **Create and activate a venv** (from `client/`):
   ```bash
   python -m venv .venv
   # macOS/Linux
   source .venv/bin/activate
   # Windows (PowerShell)
   .venv\Scripts\Activate.ps1
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirementsClient.txt
   ```

3. **Run the client** (make sure the server is already running):
   ```bash
   python client.py
   ```

4. **Usage**  
   - Type `y` to start recording, then stop with `Ctrl+C`.

---

## Database

See the **database README** for setup and usage details:  
➡️ [`server/database/README.md`](server/database/README.md)

> If your database module lives elsewhere in your fork (e.g., `backend/indexing/`), link to that folder’s `README.md` instead.

---

## Troubleshooting
 
- **Port conflicts**: change either the server port or the web dev server port, and update the env accordingly.  
- **Audio device issues**: ensure your microphone is enabled and selected; re-run the client to pick a different device.

---