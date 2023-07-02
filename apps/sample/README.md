# Microservices ()

## Techstack

- [Flask](https://flask.palletsprojects.com/en/2.3.x/)
- [Google-TTS](https://cloud.google.com/speech-to-text)
- [Whisper-STT](https://openai.com/research/whisper)

## Requirements

Install the required dependencies listed on requirements.txt: `pip install -r requirements.txt` or `pnpm postinstall`.<br>
If you face issues make sure packages are installed (`pip show <packagename>`). Also try to install with `python3 -m pip install -r requirements.txt`.

## Deployment

### Development

`pnpm dev`

### Production

Isolated Deployment

1. Build Dockerimage: `docker build -t microservices`
2. Run: `docker run --env-file ../../.env microservices`
