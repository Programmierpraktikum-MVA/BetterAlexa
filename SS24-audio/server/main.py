from uvicorn import run

# run server with functionality defined in `service.py`
if __name__ == "__main__":
    try:
        run("service:app", host="0.0.0.0", port=8006, log_level="info", workers=1)
    except KeyboardInterrupt:
        print("Server stopped.")
