from fastapi import APIRouter, HTTPException

import logging
from pydantic import BaseModel
from database.database_wrapper import get_user_id_by_meeting_id, set_meeting_id, set_sensitive_data, login_user, create_user  # Passe "database" ggf. an deinen Modulnamen an

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
                set_meeting_id(data.user_id, meeting_id)
            else:
                set_sensitive_data(data.user_id, key, str(value), data.password)
        return {"status": "success"}
    except HTTPException as e:
        raise e

@router.post("/login")
async def login(data: LoginPayload):
    """
    Simple login.  On success we cache the Zoom password under the *user_id*
    so the stream pipeline has a fallback key if no meeting-ID was cached yet.
    """
    logging.debug("Login-Versuch: %s", data)

    if not login_user(data.user_id, data.password):
        raise HTTPException(status_code=403, detail="Login fehlgeschlagen")

    ZOOM_PWD_CACHE[data.user_id] = data.password        
    return {"status": "login success"}


@router.post("/create-user")
def create_user_endpoint(data: LoginPayload):
    print("Neuer User wird erstellt:", data)
    try:
        create_user(data.user_id, data.password)
        return {"status": "user created"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/zoom/password/{meeting_id}", response_model=PwdOut, tags=["zoom"])
def get_password(meeting_id: str):
    """
    Return the cached password (404 if not present or expired).
    """
    pwd = ZOOM_PWD_CACHE.get(get_user_id_by_meeting_id(meeting_id))
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
