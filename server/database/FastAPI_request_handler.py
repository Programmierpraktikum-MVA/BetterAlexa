"""
Helper endpoints for user settings and Zoom password cache.
Loaded by service.py and mounted there.
"""

import os, logging
from fastapi import APIRouter, HTTPException           # APIRouter instead of FastAPI
from pydantic import BaseModel
from cachetools import TTLCache

# absolute, package-agnostic imports
from database.database_wrapper import (
    set_sensitive_data,
    login_user,
    create_user,
    set_zoom_link,
)



PWD_TTL_SECONDS = int(os.getenv("PWD_TTL", 60*60))
ZOOM_PWD_CACHE  = TTLCache(maxsize=1_000, ttl=PWD_TTL_SECONDS)

router = APIRouter() 

router.add_middleware(
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


@router.post("/save-settings")
async def save_settings(data: SettingsPayload):
    """
    Persist user settings and, for Zoom, also:
      • store the plain-text link in the users table          (set_zoom_link)
      • keep encrypted copies of link / meeting_id / password (set_sensitive_data)
      • cache the password in RAM for quick lookup            (/zoom/cache_password)
    """
    print("Neue Anfrage bei /save-settings angekommen:", data)

    for key, value in data.settings.items():
        if key == "zoom_link":
            # split the invite into meeting-ID and pwd
            meeting_id, pwd = parse_link(value)

            # ① write the link into the `users.zoom_link` column
            set_zoom_link(data.user_id, value)                         

            # ② store encrypted copies
            set_sensitive_data(data.user_id, key, str(value), data.password)
            set_sensitive_data(data.user_id, "zoom_meeting_id", meeting_id, data.password)
            set_sensitive_data(data.user_id, "zoom_password",   pwd,         data.password)

            # ③ cache the password under the real meeting-ID
            await app.state.httpx.post(
                "http://127.0.0.1:8000/zoom/cache_password",
                json={"meeting_id": meeting_id, "password": pwd},
                timeout=2.0,
            )
        else:
            # any other setting → just encrypt & store
            set_sensitive_data(data.user_id, key, str(value), data.password)

    return {"status": "success"}

@router.post("/login")
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


# This is copy pasted from service.py for import reasons
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