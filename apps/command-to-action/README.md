# Command to Action Microservice

## Techstack

- [Langchain](https://python.langchain.com/docs/get_started/introduction.html)
- [GPT](https://platform.openai.com/docs/api-reference/introduction)
- [Flask](https://flask.palletsprojects.com/en/2.3.x/)

## Requirements

Install the required dependencies listed on requirements.txt: `pip install -r requirements.txt` or `pnpm postinstall`.<br>
If you face issues make sure packages are installed (`pip show <packagename>`). Also try to install with `python3 -m pip install -r requirements.txt`.

## Deployment

### Development

`pnpm dev`

### Production

Isolated Deployment

1. Build Dockerimage: `docker build -t cta`
2. Run: `docker run --env-file ../../.env cta`

<!-- TODO ## Current Tools -->
