FROM python:3.11-slim

WORKDIR /app

# copy parameters and scripts from root
COPY . .

# Install dependencies for llama 3 and function calling without caching installation files (to reduce Docker image size)
RUN pip install --no-cache-dir -r requirementsServer.txt

# Run the FastAPI app
CMD ["uvicorn", "fastapi_llama3:app", "--host", "0.0.0.0", "--port", "8007"]
