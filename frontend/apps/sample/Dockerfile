FROM python:3.9

WORKDIR /app

COPY requirements.txt .

RUN apt-get update
RUN apt-get install -y ffmpeg

RUN pip install -r requirements.txt

COPY . .

EXPOSE 3001
CMD ["python3", "api/index.py"]