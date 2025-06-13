from uvicorn import run as _run
import argparse, os, platform
from zoom_joiner import join_zoom_meeting
import threading

# from discord_bot import start_discord_bot

# Verwende service.py als Uvicorn-App
APP = "service:app"

def join_zoom_meeting_on_start():
    """
    Zoom-Meeting automatisch beim Serverstart beitreten.
    """
    meeting_link = "https://us05web.zoom.us/j/81166204833?pwd=MKJ1nbafwVeEDWbOeGzdiZb3FPbAnv.1"
    print("Trete Zoom-Meeting bei...")

#    try:
#        join_zoom_meeting(meeting_link)
#        print("Zoom-Meeting erfolgreich gestartet.")
#    except Exception as e:
#        print(f"Fehler beim Beitreten des Zoom-Meetings: {e}")

def main():
    # Argumente parsen
    p = argparse.ArgumentParser()
    p.add_argument("--tcp", action="store_true",
                   help="Bind on 0.0.0.0:8006 instead of /tmp/ai.sock")
    p.add_argument("--port", type=int, default=8006)
    p.add_argument("--host", default="0.0.0.0")
    args = p.parse_args()

    # Starte Zoom-Meeting parallel
    zoom_thread = threading.Thread(target=join_zoom_meeting_on_start)
    zoom_thread.start()

    # Starte Discord-Bot parallel (importiert von discord_bot.py)
    discord_thread = threading.Thread(target=start_discord_bot)
    discord_thread.start()

    # Starte Server je nach Modus
    if args.tcp:
        print(f"Starting on TCP {args.host}:{args.port}")
        _run(APP, host=args.host, port=args.port, log_level="info")
    else:
        uds_path = os.getenv("AI_SOCKET", "/tmp/ai.sock")
        print(f"Starting on UDS {uds_path}")
        _run(APP, uds=uds_path, log_level="info")

if __name__ == "__main__":
    main()


"""
Alle Commits mit 'Bot joint automatisch einem Zoom-Meeting' als Commit Messge dürfen auskommentiert werden, diese sind noch nicht funktional
"""
