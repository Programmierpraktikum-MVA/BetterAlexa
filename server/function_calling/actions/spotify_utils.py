import datetime
import urllib
import sqlite3
from urllib import parse
import base64
import json
import requests
from requests import post, get
# from flask import Flask, redirect, request, session, jsonify
import webbrowser
from threading import Timer, Event
from .actions.database_handling import write_to_store, read_from_store, delete_from_store

#client_id = "0fa32183ad404b22bf2587006b50421f"
client_id = "642551fcd12a4d17898ce7f8310fcaa2"
#client_secret = "53520c39acb44b16962a58df6bd94e8e"
client_secret = "d93f08d1b5f944deacac371acff85ee0"
redirect_uri = "http://108.181.203.191:3001/callback"
TOKEN_URL = 'https://accounts.spotify.com/api/token'
API_BASE_URL = 'https://api.spotify.com/v1/'
current_session = {
    'access_token': '',
    'refresh_token': '',
    'expires_at': ''
}

# hardcode username to simplify things
user = "AlexaUser"

conn = sqlite3.connect('key_value_store.db')
c = conn.cursor()

def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_64 = str(base64.b64encode(auth_bytes), "utf-8")
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token


def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000")


def open_login_flask_app():
    return None
    # Timer(1, open_browser).start()

    # # Run Flask app in a separate thread
    # import threading
    # flask_thread = threading.Thread(target=app.run, kwargs={'debug': True, 'use_reloader': False})
    # flask_thread.start()

    # # Wait until the token is received
    # token_received_event.wait()

    # # Stop the Flask server (optional, if needed)
    # # request.environ.get('werkzeug.server.shutdown')()

    # return token_info

### END OF FLASK APP, FUNCS START HERE

def play_artist(artist: str):
    token_inf = get_token_inf(user)
    if is_token_expired(token_inf):
        token_inf = standard_refresh(token_inf)
    access_token = token_inf["access_token"]
    
    token = get_token()
    idee = search_for_artist(token, artist)
    context_uri = "spotify:artist:" + idee
    headers = {
        'Authorization': f"Bearer {access_token}",
        'Accept': "application/json",
        'Content-Type': "application/json"
    }
    req_body = {
        'context_uri': context_uri
    }
    response = requests.put(API_BASE_URL + 'me/player/play', headers=headers, json=req_body)
    if response.status_code == 204:
        return "the artist is successfully being played"
    else:
        return "the artist was not played successfully"

def play_album(album: str):
    token_inf = get_token_inf(user)
    if is_token_expired(token_inf):
        token_inf = standard_refresh(user, token_inf)
    access_token = token_inf["access_token"]

    token = get_token()
    idee = search_for_album(token, album)
    context_uri = "spotify:album:" + idee
    headers = {
        'Authorization': f"Bearer {access_token}",
        'Accept': "application/json",
        'Content-Type': "application/json"
    }
    req_body = {
        'context_uri': context_uri
    }
    response = requests.put(API_BASE_URL + 'me/player/play', headers=headers, json=req_body)
    if response.status_code == 204:
        return "the album was played successfully"
    else:
        return "the album was not played successfully"

def play_song(song: str):
    token_inf = get_token_inf(user)
    if is_token_expired(token_inf):
      token_inf = standard_refresh(user, token_inf)
    access_token = token_inf["access_token"]

    token = get_token()
    idee = search_for_song(token, song)
    print(idee)
    context_uri = "spotify:track:" + idee
    headers = {
        'Authorization': f"Bearer {access_token}",
        'Accept': "application/json",
        'Content-Type': "application/json"
    }
    req_body = {
        'uris': [context_uri]
    }
    response = requests.put(API_BASE_URL + 'me/player/play', headers=headers, json=req_body)
    if response.status_code == 204:
        return "song was played successfully"
    else:
        return "song was not played successfully"

def next():
    token_inf = get_token_inf(user)
    if is_token_expired(token_inf):
        token_inf = standard_refresh(token_inf)
    access_token = token_inf["access_token"]

    headers = {
        'Authorization': f"Bearer {access_token}"
    }
    response = requests.post(API_BASE_URL + 'me/player/next', headers=headers)
    if response.status_code == 204:
        return "the next song was played successfully"
    else:
        return "the next song was not played successfully"

def prev():
    token_inf = get_token_inf(user)
    if is_token_expired(token_inf):
        token_inf = standard_refresh(token_inf)
    access_token = token_inf["access_token"]    

    headers = {
        'Authorization': f"Bearer {access_token}"
    }
    response = requests.post(API_BASE_URL + 'me/player/previous', headers=headers)
    if response.status_code == 204:
        return "the previous song was played successfully"
    else:
        return "the previous song was played successfully"

def play():
    token_inf = get_token_inf(user)
    if is_token_expired(token_inf):
        token_inf = standard_refresh(token_inf)
    access_token = token_inf["access_token"]  
    
    headers = {
        'Authorization': f"Bearer {access_token}"
    }
    response = requests.put(API_BASE_URL + 'me/player/play', headers=headers)
    if response.status_code == 204:
        return "it was played successfully"
    else:
        return "it was not played successfully"
    
def pause():
    token_inf = get_token_inf(user)
    if is_token_expired(token_inf):
        token_inf = standard_refresh(token_inf)
    access_token = token_inf["access_token"]  

    headers = {
        'Authorization': f"Bearer {access_token}"
    }
    response = requests.put(API_BASE_URL + 'me/player/pause', headers=headers)
    if response.status_code == 204:
        return "it was paused successfully"
    else:
        return "it was not paused successfully"

def increase_volume(amount: int):
    token_inf = get_token_inf(user)
    if is_token_expired(token_inf):
        token_inf = standard_refresh(token_inf)
    access_token = token_inf["access_token"]

    currentstate = get_playback_state(access_token)
    vol = currentstate['device']['volume_percent']
    vol = min(vol + amount, 100)
    headers = {'Authorization': f"Bearer {access_token}"}
    url = API_BASE_URL + f"me/player/volume?volume_percent={vol}"
    response = requests.put(url, headers=headers)
    if response.status_code == 204:
        return "the volume was increased successfully"
    else:
        return "the volume was not increased successfully"

def decrease_volume(amount: int):
    token_inf = get_token_inf(user)
    if is_token_expired(token_inf):
        token_inf = standard_refresh(token_inf)
    access_token = token_inf["access_token"]

    currentstate = get_playback_state(access_token)
    vol = currentstate['device']['volume_percent']
    vol = max(vol - amount, 0)
    headers = {'Authorization': f"Bearer {access_token}"}
    url = API_BASE_URL + f"me/player/volume?volume_percent={vol}"
    response = requests.put(url, headers=headers)
    if response.status_code == 204:
        return "the volume was decreased successfully"
    else:
        return "the volume was not decreased successfully"

def add_to_queue(song: str):
    token_inf = get_token_inf(user)
    if is_token_expired(token_inf):
        token_inf = standard_refresh(token_inf)
    access_token = token_inf["access_token"]
    
    token = get_token()
    idee = search_for_song(token, song)
    context_uri = "spotify:track:" + idee
    headers = {
        'Authorization': f"Bearer {access_token}",
        'Content-Type': "application/json"
    }
    url = API_BASE_URL + f'me/player/queue?uri={context_uri}'
    response = requests.post(url, headers=headers)
    if response.status_code == 204:
        return "the song was successfully added to the queue"
    else:
        return "the song was not added to the queue successfully"

### HELPER FUNCTIONS

def search_for_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = {"Authorization": "Bearer " + token}
    query = f"?q={artist_name}&type=artist&limit=1"
    query_url = url + query
    result = requests.get(query_url, headers=headers)
    json_result = result.json()
    ide = json_result['artists']['items'][0]['id']
    return ide

def search_for_album(token, album_name):
    url = "https://api.spotify.com/v1/search"
    headers = {"Authorization": "Bearer " + token}
    query = f"?q={album_name}&type=album&limit=1"
    query_url = url + query
    result = requests.get(query_url, headers=headers)
    json_result = result.json()
    ide = json_result['albums']['items'][0]['id']
    return ide

def get_playback_state(access_token):
    headers = {
        'Authorization': f"Bearer {access_token}"
    }
    response = requests.get(API_BASE_URL + 'me/player', headers=headers)
    return response.json()


def get_playlists(access_token):
    headers = {
        'Authorization': f"Bearer {access_token}"
    }

    response = requests.get(API_BASE_URL + 'me/playlists', headers=headers)

    return response.json()


def get_available_devices(access_token):
    headers = {
        'Authorization': f"Bearer {access_token}"
    }
    response = requests.get(API_BASE_URL + 'me/player/devices', headers=headers)
    try:
        return response.json()
    except Exception as e:
        return {}

def search_for_song(token, song_name):
    url = "https://api.spotify.com/v1/search"
    headers = {"Authorization": "Bearer " + token}
    query = f"?q={song_name}&type=track&limit=1"
    query_url = url + query
    result = requests.get(query_url, headers=headers)
    json_result = result.json()
    ide = json_result['tracks']['items'][0]['id']
    return ide

def is_token_expired(token_inf):
    return 'error' in get_available_devices(token_inf['access_token'])


def standard_refresh(user, token_inf):
    req_body = {
        'grant_type': 'refresh_token',
        'refresh_token': token_inf['refresh_token'],
        'client_id': client_id,
        'client_secret': client_secret
    }
    response = requests.post(TOKEN_URL, data=req_body)
    write_to_store(user, json.dumps(response.json()), conn, c)
    return response.json()

def get_token_inf(user):
    if read_from_store(user,c) is not None:
        toke_dump = read_from_store(user, c)
        return json.loads(toke_dump)
    else:
        toke_inf = open_login_flask_app()
        write_to_store(user, json.dumps(toke_inf), conn, c)
        return toke_inf
