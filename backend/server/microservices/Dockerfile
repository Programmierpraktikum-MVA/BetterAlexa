# Dockerfile for microservices.py
FROM python:3.11-slim
WORKDIR /app
COPY microservices.py /app
run pip install fastapi uvicorn openai-whisper gtts
CMD ["uvicorn", "microservices:app", "--host", "0.0.0.0", "--port", "8006"]
