# stub_tutorai.py
from fastapi import FastAPI, Response, Request
import uvicorn, os, json

app = FastAPI()
TOKEN = os.getenv("TUTORAI_TOKEN", "dev-token")        # must match BetterAlexa

@app.post("/api/v1/chat")
async def chat(request: Request, response: Response):
    data = await request.json()                        # {"query": "..."}
    print("⇢ stub got:", json.dumps(data))
    response.headers["Authorization"] = f"Bearer {TOKEN}"
    return {
        "answer": f"Echo: {data.get('query','')}",
        "done": True                                  # tells pipeline to leave delegate mode
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8009)
