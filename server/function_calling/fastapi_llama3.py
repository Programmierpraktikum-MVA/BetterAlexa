import json
import os
# get the functions/classes from group b,c
# from llama3 import LLama3
from fastapi import FastAPI
from starlette.responses import RedirectResponse
from pydantic import BaseModel
from requests import post

class UserInput(BaseModel):
    user_input: str

app = FastAPI()

# llamaModel = LLama3("Llama-3-8B-function-calling", "https://drive.google.com/drive/folders/1CJtn-3nCfQT3FU3pOgA3zTIdPLQ9n3x6?usp=sharing", "https://drive.google.com/drive/folders/1RmhIu2FXqwu4TxIQ9GpDtYb_IXWoVd7z?usp=sharing")

print("llama model loaded")

@app.get("/")
async def root():
    return RedirectResponse(url="/docs")

@app.post("/t2c")
async def t2c(user_data: UserInput):
    text = user_data.user_input
    output = "Did you just ask " + text + "? You dumbass!" # llamaModel.process_input(user_input)
    try:
        qdrant = post("http://108.181.203.191:8047/vidindex", json={"user_input": text})
        return {"message": output, "qdrant": qdrant.json()["message"]}
    except Exception as e:
        return {"message": output, "qdrant": "{}".format(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)
