# 🎤 BetterAlexa Thin Client

This is a lightweight client for the **BetterAlexa** voice assistant system. It captures microphone audio using VAD (voice activity detection), sends it to the BetterAlexa server, and plays the AI-generated spoken response.

---

## 🚀 Features

- 🔊 **Voice Activation**: Only records when speech is detected using `webrtcvad`.
- 📡 **Streaming Communication**: Sends captured audio to a FastAPI server.
- 🗣️ **Playback Response**: Receives `audio/wav` output and plays it using `pygame`.

---

## 📦 Requirements

Install dependencies with:

```bash
pip install -r requirementsClient.txt
