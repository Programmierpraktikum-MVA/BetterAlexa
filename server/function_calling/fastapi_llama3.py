import json
import os
# get the functions/classes from group b,c
from llama3 import LLama3
from fastapi import FastAPI, Request
from starlette.responses import RedirectResponse
from pydantic import BaseModel
from requests import post
from time import time

class UserInput(BaseModel):
    user_input: str

app = FastAPI()

llamaModel = LLama3("Llama-3-8B-function-calling", "https://drive.google.com/drive/folders/1CJtn-3nCfQT3FU3pOgA3zTIdPLQ9n3x6?usp=sharing", "https://drive.google.com/drive/folders/1RmhIu2FXqwu4TxIQ9GpDtYb_IXWoVd7z?usp=sharing")

print("llama model loaded")

@app.get("/")
async def root():
    return RedirectResponse(url="/docs")

@app.post("/t2c")
async def t2c(request: Request, user_data: UserInput):
    text = user_data.user_input
    start_time = time()
    output = llamaModel.process_input(text)
    print("llama time taken: {}".format(time() - start_time))
    #print("x-spotify-token: {}".format(request.headers.get("x-spotify-access-token", "header not found")))
    try:
        qdrant = post("http://108.181.203.191:8047/vidindex", json={"user_input": text})
        return {"message": output, "qdrant": qdrant.json()["message"]}
    except Exception as e:
        print("excepted qdrant: {}".format(e))
        return {"message": output, "qdrant": "{}".format("Sorry, I had some issues looking up relevant videos.")}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)
