FROM python:3-alpine

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

EXPOSE 3002
CMD ["python3", "api/index.py"]