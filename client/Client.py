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

import argparse
import asyncio
import io
from pathlib import Path

import httpx
import numpy as np
import pygame
import sounddevice as sd        # noqa: F401  (kept for completeness)
import soundfile as sf          # noqa: F401
import audio_interface          # your existing helper

SR = 16_000


def play_wav_bytes(wav_bytes: bytes) -> None:
    """Play a WAV byte-string through pygame."""
    buf = io.BytesIO(wav_bytes)
    pygame.mixer.init(frequency=SR)
    pygame.mixer.music.load(buf)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    pygame.mixer.quit()


async def main(args: argparse.Namespace) -> None:
    """
    Main streaming loop.

    If --local is set we build an AsyncHTTPTransport bound to the Unix socket
    (httpx/httpcore will ignore the hostname part of base_url).  Otherwise we
    fall back to a normal TCP connection to args.server.
    """
    if args.local:
        uds_path = Path(args.uds).expanduser()
        transport = httpx.AsyncHTTPTransport(uds=str(uds_path))
        base_url = "http://betteralexa"         # dummy – required but ignored
    else:
        transport = None                        # use httpx defaults (TCP)
        base_url = args.server.rstrip("/")

    async with httpx.AsyncClient(
        transport=transport,
        timeout=3000,
        base_url=base_url,
    ) as client:
        while True:
            # 1. Capture speech until VAD silence.
            pcm = audio_interface.listen_for_voice()     # blocking

            # 2. Ship it to BetterAlexa.
            payload = {
                "meeting_id": args.meeting,
                "pcm": pcm.tolist(),                     # JSON-serialisable
            }
            r = await client.post("/api/v1/stream", json=payload)
            r.raise_for_status()

            # 3. Play the assistant’s reply.
            print(f"← {len(r.content)/1024:.1f} KB audio from server – playing")
            play_wav_bytes(r.content)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--server",
        default="http://108.181.203.191:8006",
        help="Base URL of BetterAlexa FastAPI core (ignored with --local)",
    )
    ap.add_argument(
        "--local",
        action="store_true",
        help="Use Unix-domain socket transport instead of TCP",
    )
    ap.add_argument(
        "--uds",
        default="/tmp/ai.sock",
        help="Path to Unix-domain socket used by BetterAlexa (with --local)",
    )
    ap.add_argument(
        "--meeting",
        default="pv_local",
        help="Session ID used by server-side FSM",
    )
    asyncio.run(main(ap.parse_args()))