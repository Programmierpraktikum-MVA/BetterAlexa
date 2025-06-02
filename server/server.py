"""
Convenience entry-point: run

    python server.py

to start the FastAPI core on a Unix-domain socket (Linux/macOS)
"""
from uvicorn import run as _run
import os


if __name__ == "__main__":
    uds_path = os.getenv("AI_SOCKET", "/tmp/ai.sock")
    print(f"Starting core on UDS {uds_path}")
    _run(
        "core.service:app",
        uds=uds_path,
        log_level="info",
        workers=1,
    )
