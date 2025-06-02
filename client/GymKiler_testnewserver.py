#!/usr/bin/env python3
"""
thin_client_pv.py  –  PvRecorder + VAD front-end for BetterAlexa

Usage:
    python thin_client_pv.py --server http://SERVER:8006 --meeting myMeeting

Flow:
1. Calls audio_interface.listen_for_voice()  ➜  NumPy float32 (16 kHz mono)
2. POSTs   {meeting_id, pcm:[…]}   to  /api/v1/stream
3. Plays the returned  audio/wav   via sounddevice
"""

import argparse, asyncio, io, json
from pathlib import Path

import numpy as np
import httpx
import sounddevice as sd
import soundfile as sf

import audio_interface                 # ← your existing helper

SR = 16_000

def play_wav_bytes(wav_bytes: bytes):
    """Decode WAV in-memory and play via sounddevice."""
    audio, sr = sf.read(io.BytesIO(wav_bytes), dtype="float32")
    sd.play(audio, sr)
    sd.wait()

async def main(args):
    async with httpx.AsyncClient(timeout=30) as client:
        while True:
            pcm = audio_interface.listen_for_voice()      # blocks until VAD silence
            payload = {
                "meeting_id": args.meeting,
                "pcm": pcm.tolist(),                     # JSON-friendly
            }
            r = await client.post(f"{args.server}/api/v1/stream", json=payload)
            r.raise_for_status()
            print(f"← {len(r.content)/1024:.1f} KB audio from server – playing")
            play_wav_bytes(r.content)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--server", default="http://108.181.203.191:8000",
                    help="Base URL of BetterAlexa FastAPI core")
    ap.add_argument("--meeting", default="pv_local",
                    help="Session ID used by server-side FSM")
    asyncio.run(main(ap.parse_args()))
