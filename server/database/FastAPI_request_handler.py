from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .database_wrapper import set_sensitive_data, login_user, create_user  # Passe "database" ggf. an deinen Modulnamen an
from fastapi.middleware.cors import CORSMiddleware

from cachetools import TTLCache
PWD_TTL_SECONDS = int(os.getenv("PWD_TTL", 60*60))
ZOOM_PWD_CACHE  = TTLCache(maxsize=1_000, ttl=PWD_TTL_SECONDS)

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

class CachePwdIn(BaseModel):
    meeting_id: str
    password:   str

class PwdOut(BaseModel):
    meeting_id: str
    password:   str

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
async def login(data: LoginPayload):
    import httpx
    print("Login-Versuch:", data)
    if login_user(data.user_id, data.password):
        try:
            await app.state.httpx.post(           # re-uses the shared AsyncClient
                "http://127.0.0.1:8000/zoom/cache_password",
                json={"meeting_id": data.user_id, "password": data.password},
                timeout=2.0
            )
        except httpx.HTTPError as exc:
            logging.warning("Could not cache Zoom password: %s", exc)
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

@app.post("/zoom/cache_password", response_model=None, tags=["zoom"])
def cache_password(payload: CachePwdIn):
    """Store a password in RAM for `PWD_TTL_SECONDS`."""
    ZOOM_PWD_CACHE[payload.meeting_id] = payload.password
    return True

@app.get("/zoom/password/{meeting_id}", response_model=PwdOut, tags=["zoom"])
def get_password(meeting_id: str):
    """
    Return the cached password (404 if not present or expired).
    """
    pwd = ZOOM_PWD_CACHE.get(meeting_id)
    if pwd is None:
        raise HTTPException(status_code=404, detail="Password not found or expired")
    return PwdOut(meeting_id=meeting_id, password=pwd)