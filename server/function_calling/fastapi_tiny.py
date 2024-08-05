import json
import os
# get the functions/classes from group b,c
from fastapi import FastAPI, Request
from starlette.responses import RedirectResponse
from pydantic import BaseModel
from requests import post
from time import time
import actions.database_handling
import sqlite3

class UserInput(BaseModel):
    user_input: str

app = FastAPI()




@app.get("/")
async def root():
    return RedirectResponse(url="/docs")

@app.post("/t2c")
async def t2c(request: Request, user_data: UserInput):
    text = user_data.user_input
    start_time = time()
    token ={
        "access_token":request.headers.get("x-spotify-access-token", "header not found"),
        "refresh_token": request.headers.get("x-spotify-refresh-token", "header not found")
    }
    # print(token)

    conn = sqlite3.connect('key_value_store.db')
    c = conn.cursor()

    actions.database_handling.write_to_store("AlexaUser", json.dumps(token), conn, c)

    conn.close()

    output = llamaModel.process_input(text)

    conn = sqlite3.connect('key_value_store.db')
    c = conn.cursor()
    actions.database_handling.delete_from_store("AlexaUser", conn, c)
    conn.close()
    
    # print("llama time taken: {}".format(time() - start_time))
    # print("x-spotify-access-token: {}".format(request.headers.get("x-spotify-access-token", "header not found")))
    print("x-spotify-refresh-token: {}".format(request.headers.get("x-spotify-refresh-token", "header not found")))
    try:
        qdrant = post("http://108.181.203.191:8047/vidindex", json={"user_input": text})
        return {"message": output, "qdrant": qdrant.json()["message"]}
    except Exception as e:
        print("excepted qdrant: {}".format(e))
        return {"message": output, "qdrant": "{}".format("Sorry, I had some issues looking up relevant videos.")}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)
