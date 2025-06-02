from uvicorn import run as _run
import argparse, os, platform


# Use --tcp for testing with thin-client on other device. 

APP = "service:app"

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--tcp", action="store_true",
                   help="Bind on 0.0.0.0:8006 instead of /tmp/ai.sock")
    p.add_argument("--port", type=int, default=8006)
    p.add_argument("--host", default="0.0.0.0")
    args = p.parse_args()

    if args.tcp:
        print(f"Starting on TCP {args.host}:{args.port}")
        _run(APP, host=args.host, port=args.port, log_level="info")
    else:
        uds_path = os.getenv("AI_SOCKET", "/tmp/ai.sock")
        print(f"Starting on UDS {uds_path}")
        _run(APP, uds=uds_path, log_level="info")

if __name__ == "__main__":
    main()
