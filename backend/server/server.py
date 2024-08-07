from uvicorn import run

# run server with functionality defined in `service.py`
if __name__ == "__main__":
    try:
        run("service:app", host="127.0.0.1", port=8006, log_level="info", workers=1)
    except KeyboardInterrupt:
        print("Server stopped.")
