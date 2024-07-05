from fastapi import FastAPI
from starlette.responses import RedirectResponse
import uvicorn
import os
import loadqdrant

app = FastAPI()

@app.get("/")
async def root():
    return RedirectResponse(url="/docs")
@app.post("/vidindex/{user_input}")
async def vidindex(user_input: str):
    response = loadqdrant.queryCollection(user_input, 'MVA')
    return {'message': response}

if __name__ == "__main__":
    uvicorn.run(app, hostname="0.0.0.0", port=8047)