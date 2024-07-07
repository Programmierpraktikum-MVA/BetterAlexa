from fastapi import FastAPI
from starlette.responses import RedirectResponse
import uvicorn
import os
import loadqdrant
from pydantic import BaseModel

app = FastAPI()

class UserInput(BaseModel):
    user_input: str

@app.get("/")
async def root():
    return RedirectResponse(url="/docs")
@app.post("/vidindex")
async def vidindex(input_data: UserInput):
    output = loadqdrant.queryCollection(input_data.user_input, 'MVA')
    print(f"Output of Qdrant: {output}")
    return {"message": output}

if __name__ == "__main__":
    uvicorn.run(app,host="0.0.0.0", port=8047)
