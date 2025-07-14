from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .database_wrapper import set_sensitive_data, login_user, create_user  # Passe "database" ggf. an deinen Modulnamen an
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # für Tests, später einschränken!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SettingsPayload(BaseModel):
    user_id: str
    password: str
    settings: dict

class LoginPayload(BaseModel):
    user_id: str
    password: str

@app.post("/save-settings")

def save_settings(data: SettingsPayload):
    print("Neue Anfrage bei /save-settings angekommen:", data)
    try:
        # Jedes Key-Value-Paar als sensibles Datum abspeichern
        for key, value in data.settings.items():
            set_sensitive_data(data.user_id, key, str(value), data.password)
        return {"status": "success"}
    except HTTPException as e:
        raise e

@app.post("/login")
def login(data: LoginPayload):
    print("Login-Versuch:", data)
    if login_user(data.user_id, data.password):
        return {"status": "login success"}
    else:
        raise HTTPException(status_code=403, detail="Login fehlgeschlagen")

@app.post("/create-user")
def create_user_endpoint(data: LoginPayload):
    print("Neuer User wird erstellt:", data)
    try:
        create_user(data.user_id, data.password)
        return {"status": "user created"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
