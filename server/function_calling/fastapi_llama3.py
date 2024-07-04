import json
import os
# get the functions/classes from group b,c
from llama3 import LLama3
from fastapi import FastAPI
from starlette.responses import RedirectResponse

app = FastAPI()

llamaModel = LLama3("Llama-3-8B-function-calling", "https://drive.google.com/drive/folders/1CJtn-3nCfQT3FU3pOgA3zTIdPLQ9n3x6?usp=sharing", "https://drive.google.com/drive/folders/1RmhIu2FXqwu4TxIQ9GpDtYb_IXWoVd7z?usp=sharing")

print("llama model loaded")

@app.get("/")
async def root():
    return RedirectResponse(url="/docs")

@app.post("/t2c/{user_input}")
async def t2c(user_input: str):
    output = llamaModel.process_input(user_input)
    return {"message": output}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, hostname="0.0.0.0", port=8007)
