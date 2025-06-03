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
import pygame
import audio_interface                 # ← your existing helper

SR = 16_000

def play_wav_bytes(wav_bytes):
    buf = io.BytesIO(wav_bytes)
    pygame.mixer.init(frequency=SR)
    pygame.mixer.music.load(buf)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    pygame.mixer.quit()

async def main(args):
    async with httpx.AsyncClient(timeout=3000) as client:
        while True:
            pcm = audio_interface.listen_for_voice()      # blocks until VAD silence
            payload = {
                "meeting_id": args.meeting,
                "pcm": pcm.tolist(),                     # JSON-friendly
            }
            r = await client.post(f"{args.server}/api/v1/stream", json=payload)
            r.raise_for_status()
            print(f"← {len(r.content)/1024:.1f} KB audio from server – playing")
            wav_bytes = r.content          # r is the Response
            play_wav_bytes(wav_bytes)
            

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--server", default="http://108.181.203.191:8006",
                    help="Base URL of BetterAlexa FastAPI core")
    ap.add_argument("--meeting", default="pv_local",
                    help="Session ID used by server-side FSM")
    asyncio.run(main(ap.parse_args()))
