import datetime
import urllib
import sqlite3
from urllib import parse
import base64
import json
import requests
from requests import post, get
from flask import Flask, redirect, request, session, jsonify
import webbrowser
from threading import Timer, Event
from actions.database_handling import write_to_store, read_from_store, delete_from_store

client_id = "0fa32183ad404b22bf2587006b50421f"
client_secret = "53520c39acb44b16962a58df6bd94e8e"
redirect_uri = "http://127.0.0.1:5000/callback"
TOKEN_URL = 'https://accounts.spotify.com/api/token'
API_BASE_URL = 'https://api.spotify.com/v1/'
current_session = {
    'access_token': '',
    'refresh_token': '',
    'expires_at': ''
}

acc = "BQADF-7Khe4mdlCjBh5CVd0CY46S-iCzcHya7jA9LZVJyQRCrAfxTAwDE9MBiphh1rRcOc7AvvUDIKqGxG4ABppJZIjKtP52p6VP_PIaBb-74emdB8kJcbH7Qu8NnDsP3h5o1d-zHIPqxgpSovyRaRDLvw56fSxT3JGnOAdGsN16ZWB8ybdym5geb2dgEbpxQ7jghOVsbarT6UIwjT2KmH5spKnnBdyvQgiaty-HYC-3t_Rg9PpzuFlhZOL3yqlcIEhgHhVIkdTSpo8FbxhXwtGBNKYoLRYQ58yCBFsKbcuG"
app = Flask(__name__)
app.secret_key = 'asljfghsaldaslkas'
app.config['SESSION_COOKIE_NAME'] = 'Spotify Cookie'

conn = sqlite3.connect('key_value_store.db')
c = conn.cursor()

# Create table
c.execute('''CREATE TABLE IF NOT EXISTS store
             (key TEXT PRIMARY KEY, value TEXT)''')

# Global variable to store token information
token_info = None
token_received_event = Event()



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
    Timer(1, open_browser).start()

    # Run Flask app in a separate thread
    import threading
    flask_thread = threading.Thread(target=app.run, kwargs={'debug': True, 'use_reloader': False})
    flask_thread.start()

    # Wait until the token is received
    token_received_event.wait()

    # Stop the Flask server (optional, if needed)
    # request.environ.get('werkzeug.server.shutdown')()

    return token_info


@app.route('/')
def index():
    return ("Welcome to AILEXA! \n"
            "Please <a href='/login'>log in to your Spotify account</a>")


@app.route('/login')
def auth_user():
    query_params = {
        'response_type': 'code',
        'client_id': client_id,
        'scope': 'user-modify-playback-state '
                 'user-read-private '
                 'user-read-email '
                 'user-library-read '
                 'playlist-read-private '
                 'playlist-modify-public '
                 'playlist-modify-private '
                 'user-read-playback-state ',
        'redirect_uri': redirect_uri,
        'show_dialog': True  # SET TO FALSE WHEN DONE
    }
    query_string = urllib.parse.urlencode(query_params)
    auth_url = f'https://accounts.spotify.com/authorize?{query_string}'
    return redirect(auth_url)


@app.route('/callback')
def callback():
    global token_info
    if 'error' in request.args:
        return jsonify({"error": request.args['error']})
    if 'code' in request.args:
        req_body = {
            'code': request.args['code'],
            'grant_type': 'authorization_code',
            'redirect_uri': redirect_uri,
            'client_id': client_id,
            'client_secret': client_secret
        }
        auth_string = f"{client_id}:{client_secret}"
        auth_bytes = auth_string.encode('utf-8')
        auth_base64 = base64.b64encode(auth_bytes).decode('utf-8')
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f"Basic {auth_base64}"
        }
        response = requests.post('https://accounts.spotify.com/api/token', headers=headers, data=req_body)
        token_info = response.json()
        session['access_token'] = token_info['access_token']
        session['refresh_token'] = token_info['refresh_token']
        session['expires_at'] = datetime.datetime.now().timestamp() + token_info['expires_in']

        # Signal that the token has been received
        token_received_event.set()

        return redirect('/finalwindow')
    return 'No code provided', 400


# if access token has expired
@app.route('/refresh-token')
def refresh_token():
    if 'refresh_token' not in session:
        return redirect('/login')

    if datetime.datetime.now().timestamp() > session['expires_at']:
        req_body = {
            'grant_type': 'refresh_token',
            'refresh_token': session['refresh_token'],
            'client_id': client_id,
            'client_secret': client_secret
        }
    response = requests.post(TOKEN_URL, data=req_body)
    new_token_info = response.json()
    session['access_token'] = new_token_info['access_token']
    session['expires_at'] = datetime.datetime.now().timestamp() + new_token_info['expires_in']
    current_session['access_token'] = new_token_info['access_token']
    current_session['expires_at'] = datetime.datetime.now().timestamp() + new_token_info['expires_in']

    return redirect('/playlists')


@app.route('/finalwindow')
def final_window():
    if 'access_token' not in session:
        return redirect('/login')
    return "Thank you for logging in, you may close this window now!"


# END OF FLASK APP, FUNCS START HERE


def search_for_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = {"Authorization": "Bearer " + token}
    query = f"?q={artist_name}&type=artist&limit=1"
    query_url = url + query
    result = requests.get(query_url, headers=headers)
    json_result = result.json()
    ide = json_result['artists']['items'][0]['id']
    return ide


def play_artist(access_token, artist):
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
    return response

def user_play_artist(user, artist):
    token_inf = get_token_inf(user)
    if is_token_expired(token_inf):
        token_inf = standard_refresh(token_inf)
    return play_song(token_inf['access_token'], artist)

def search_for_album(token, album_name):
    url = "https://api.spotify.com/v1/search"
    headers = {"Authorization": "Bearer " + token}
    query = f"?q={album_name}&type=album&limit=1"
    query_url = url + query
    result = requests.get(query_url, headers=headers)
    json_result = result.json()
    ide = json_result['albums']['items'][0]['id']
    return ide


def play_album(access_token, album):
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
    return response

def user_play_album(user, album):
    token_inf = get_token_inf(user)
    if is_token_expired(token_inf):
        token_inf = standard_refresh(user, token_inf)
    return play_album(token_inf['access_token'], album)

"""
def get_similar_artist(token, artist_name):
    json_result = search_for_artist(token, artist_name)
    print(json_result)
    similar_url = json_result['next']
    result = get(similar_url, headers=(token))
    similars = json.loads(result.content)
    print(similars)
"""


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
    return response.json()


def next(access_token):
    headers = {
        'Authorization': f"Bearer {access_token}"
    }
    response = requests.post(API_BASE_URL + 'me/player/next', headers=headers)
    return response

def user_next(user):
    token_inf = get_token_inf(user)
    if is_token_expired(token_inf):
        token_inf = standard_refresh(token_inf)
    return next(token_inf['access_token'])

def prev(access_token):
    headers = {
        'Authorization': f"Bearer {access_token}"
    }
    response = requests.post(API_BASE_URL + 'me/player/previous', headers=headers)
    return response

def user_prev(user):
    token_inf = get_token_inf(user)
    if is_token_expired(token_inf):
        token_inf = standard_refresh(token_inf)
    return prev(token_inf['access_token'])

def pause(access_token):
    headers = {
        'Authorization': f"Bearer {access_token}"
    }
    response = requests.put(API_BASE_URL + 'me/player/pause', headers=headers)
    return response

def user_pause(user):
    token_inf = get_token_inf(user)
    if is_token_expired(token_inf):
        token_inf = standard_refresh(token_inf)
    return pause(token_inf['access_token'])

def play(access_token):
    headers = {
        'Authorization': f"Bearer {access_token}"
    }
    response = requests.put(API_BASE_URL + 'me/player/play', headers=headers)
    return response

def user_play(user):
    token_inf = get_token_inf(user)
    if is_token_expired(token_inf):
        token_inf = standard_refresh(token_inf)
    return play(token_inf['access_token'])

def search_for_song(token, song_name):
    url = "https://api.spotify.com/v1/search"
    headers = {"Authorization": "Bearer " + token}
    query = f"?q={song_name}&type=track&limit=1"
    query_url = url + query
    result = requests.get(query_url, headers=headers)
    json_result = result.json()
    ide = json_result['tracks']['items'][0]['id']
    return ide


def play_song(access_token, song):
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
    return response

def user_play_song(user, song):
    token_inf = get_token_inf(user)
    if is_token_expired(token_inf):
      token_inf = standard_refresh(user, token_inf)
    return play_song(token_inf['access_token'], song)

def increase_volume(access_token):
    currentstate = get_playback_state(access_token)
    vol = currentstate['device']['volume_percent']
    print(vol)
    vol = vol + 15
    if vol > 100:
        vol = 100
    headers = {'Authorization': f"Bearer {access_token}"}
    url = API_BASE_URL + f"me/player/volume?volume_percent={vol}"
    response = requests.put(url, headers=headers)
    return response

def user_increase_volume(user):
    token_inf = get_token_inf(user)
    if is_token_expired(token_inf):
        token_inf = standard_refresh(token_inf)
    return increase_volume(token_inf['access_token'])

def decrease_volume(access_token):
    currentstate = get_playback_state(access_token)
    vol = currentstate['device']['volume_percent']
    if vol > 20:
        vol = vol - 15
    else:
        vol = vol / 2
    headers = {'Authorization': f"Bearer {access_token}"}
    url = API_BASE_URL + f"me/player/volume?volume_percent={vol}"
    response = requests.put(url, headers=headers)
    return response

def user_decrease_volume(user):
    token_inf = get_token_inf(user)
    if is_token_expired(token_inf):
        token_inf = standard_refresh(token_inf)
    return decrease_volume(token_inf['access_token'])


def set_volume_to(access_token, vol):  # Takes user access token and desired volume in percent (0-100 including)
    headers = {'Authorization': f"Bearer {access_token}"}
    url = API_BASE_URL + f"me/player/volume?volume_percent={vol}"
    response = requests.put(url, headers=headers)
    return response

def user_set_volume_to(user, vol):
    token_inf = get_token_inf(user)
    if is_token_expired(token_inf):
        token_inf = standard_refresh(token_inf)
    return set_volume_to(token_inf['access_token'], vol)


def add_to_queue(access_token, song):
    token = get_token()
    idee = search_for_song(token, song)
    context_uri = "spotify:track:" + idee
    headers = {
        'Authorization': f"Bearer {access_token}",
        'Content-Type': "application/json"
    }
    url = API_BASE_URL + f'me/player/queue?uri={context_uri}'
    response = requests.post(url, headers=headers)
    return response

def user_add_to_queue(user, song):
    token_inf = get_token_inf(user)
    if is_token_expired(token_inf):
        token_inf = standard_refresh(token_inf)
    return add_to_queue(token_inf['access_token'], song)

def turn_on_shuffle(access_token):
    headers = {'Authorization': f"Bearer {access_token}"}
    response = requests.put(API_BASE_URL + 'me/player/shuffle?state=true', headers=headers)
    return response

def user_turn_on_shuffle(user):
    token_inf = get_token_inf(user)
    if is_token_expired(token_inf):
        token_inf = standard_refresh(token_inf)
    return turn_on_shuffle(token_inf['access_token'])

def turn_off_shuffle(access_token):
    headers = {'Authorization': f"Bearer {access_token}"}
    response = requests.put(API_BASE_URL + 'me/player/shuffle?state=false', headers=headers)
    return response

def user_turn_off_shuffle(user):
    token_inf = get_token_inf(user)
    if is_token_expired(token_inf):
        token_inf = standard_refresh(token_inf)
    return turn_off_shuffle(token_inf['access_token'])

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



#user_play_album("Emil", "selected ambient works 85-92")
# open_login_flask_app()
# print(play_song(acc, "under pressure").content)
# print(play_artist(acc, "michael jackson").content)
# print(play_album(acc, "selected ambient works 85-92").content)
# print(increase_volume(acc).content)
# print(decrease_volume(acc).content)
# print(set_volume_to(acc, 70).content)
# print(turn_off_shuffle(acc).content)
# print(turn_on_shuffle(acc).content)
# print(next(acc).content)
# print(prev(acc).content)
# print(pause(acc).content)
# print(play(acc).content)
# print(add_to_queue(acc, "under pressure"))
# print(open_login_flask_app())
#print(open_login_flask_app())