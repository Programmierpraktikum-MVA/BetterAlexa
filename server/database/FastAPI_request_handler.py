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
from urllib.parse import urlparse, parse_qs
from typing import Tuple, Optional

def parse_link(link: str) -> Tuple[str, Optional[str]]:
    """
    Extract the Zoom meeting-ID and optional password from an invite URL.

    Returns
    -------
    meeting_id : str            e.g. '12345678901'
    password   : Optional[str]  e.g. 'Q2pWc1lRbGxybGg0' or None
    """
    parsed = urlparse(link)

    # --- meeting-ID --------------------------------------------------------
    # Path examples: '/j/12345678901', '/s/12345678901', '/w/12345678901'
    path_parts = [p for p in parsed.path.split('/') if p]          # drop ''
    meeting_id = None
    for token in ('j', 's', 'w'):                                  # common tokens
        if token in path_parts:
            idx = path_parts.index(token) + 1
            if idx < len(path_parts):
                meeting_id = path_parts[idx]
                break
    if meeting_id is None:                                         # fallback
        for part in reversed(path_parts):
            if part.isdigit():
                meeting_id = part
                break
    if meeting_id is None:
        raise ValueError(f"Could not find meeting-id in link: {link}")

    # --- password (query string) ------------------------------------------
    pwd = parse_qs(parsed.query).get("pwd", [None])[0]

    return meeting_id, pwd
