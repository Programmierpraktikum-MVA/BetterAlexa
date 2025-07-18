from fastapi import APIRouter, HTTPException


from pydantic import BaseModel
from database_wrapper import set_sensitive_data, login_user, create_user  # Passe "database" ggf. an deinen Modulnamen an

import os
from cachetools import TTLCache
PWD_TTL_SECONDS = int(os.getenv("PWD_TTL", 60*60))
ZOOM_PWD_CACHE  = TTLCache(maxsize=1_000, ttl=PWD_TTL_SECONDS)

router = APIRouter()

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

@router.post("/save-settings")

def save_settings(data: SettingsPayload):
    print("Neue Anfrage bei /save-settings angekommen:", data)
    try:
        # Jedes Key-Value-Paar als sensibles Datum abspeichern
        for key, value in data.settings.items():
            if key == "zoom_link":
                meeting_id, pwd = parse_link(value)
                set_sensitive_data(data.user_id, key, str(value), data.password)
                # Meeting-ID und Passwort separat speichern
                set_sensitive_data(data.user_id, "zoom_meeting_id", meeting_id, data.password)
                set_sensitive_data(data.user_id, "zoom_password", pwd, data.password)
            else:
                set_sensitive_data(data.user_id, key, str(value), data.password)
        return {"status": "success"}
    except HTTPException as e:
        raise e

@router.post("/login")
async def login(data: LoginPayload):
    import httpx
    print("Login-Versuch:", data)
    if login_user(data.user_id, data.password):
        try:
            await httpx.post(           # re-uses the shared AsyncClient
                "http://127.0.0.1:8000/zoom/cache_password",
                json={"meeting_id": data.user_id, "password": data.password},
                timeout=2.0
            )
        except httpx.HTTPError as exc:
            logging.warning("Could not cache Zoom password: %s", exc)
        return {"status": "login success"}
    else:
        raise HTTPException(status_code=403, detail="Login fehlgeschlagen")

@router.post("/create-user")
def create_user_endpoint(data: LoginPayload):
    print("Neuer User wird erstellt:", data)
    try:
        create_user(data.user_id, data.password)
        return {"status": "user created"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/zoom/cache_password", response_model=None, tags=["zoom"])
def cache_password(payload: CachePwdIn):
    """Store a password in RAM for `PWD_TTL_SECONDS`."""
    ZOOM_PWD_CACHE[payload.meeting_id] = payload.password
    return True

@router.get("/zoom/password/{meeting_id}", response_model=PwdOut, tags=["zoom"])
def get_password(meeting_id: str):
    """
    Return the cached password (404 if not present or expired).
    """
    pwd = ZOOM_PWD_CACHE.get(meeting_id)
    if pwd is None:
        raise HTTPException(status_code=404, detail="Password not found or expired")
    return PwdOut(meeting_id=meeting_id, password=pwd)


#From service.py, import stuff
def parse_link(link: str):
    """
    Takes a zoom meeting invite link and returns the included meeting id and password.
    
    Args:
        link (str): The full zoom invite link.

    Returns:
        meeting_id: The Meeting ID for the zoom meeting.
        pwd: The Password for the zoom meeting.
    """
    parts = link.split("/")
    meeting_id, pwd = parts[4].split("?")
    #meeting_id = meeting_id[0:3] + ' ' + meeting_id[3:7] + ' ' + meeting_id[7:10]

    end = len(pwd) -2
    pwd = pwd[4:end]
    return meeting_id,pwd
