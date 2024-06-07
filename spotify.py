import datetime
import urllib
from urllib import parse
import base64
import json
import requests
from requests import post, get
from flask import Flask, redirect, request, session, jsonify
import webbrowser
from threading import Timer


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

acc = "BQDFW5fU82lXPAON7yzRjo0bHnIka3d2WYPKI9uxdyOEkQjPUrLU9vYKykfw2UMEJrwuBznkGBH4yiHSshQp5y8u09f8FO3399Gsbd4LxjjMRGpzOj4rMDddAiVu9oOhyudB6IpFk9BUM9QLXpF24Qf_BLgEyYiySaeoC5JJRKVXrzecYqTUwtg3D7Xv52rgEsOqJ9xJWGEWmICAKfnp5ccokWSjKmEqyKIKnQalW9WOVZn4hh0dK2nkhr1cPaEztXMHpeCy4QGq4zFDlJ34uDP3CRf9aAXh08LlokZKWg8y"
app = Flask(__name__)
app.secret_key = 'asljfghsaldaslkas'
app.config['SESSION_COOKIE_NAME'] = 'Spotify Cookie'
TOKEN_INFO = 'token_info'


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
    app.run() #REMOVE DEBUG MODE WHEN DONE



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
        'show_dialog': True # SET TO FALSE WHEN DONE
    }
    query_string = urllib.parse.urlencode(query_params)
    auth_url = f'https://accounts.spotify.com/authorize?{query_string}'
    return redirect(auth_url)


@app.route('/callback')
def callback():
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

        current_session['access_token'] = token_info['access_token']
        current_session['refresh_token'] = token_info['refresh_token']
        current_session['expires_at'] = datetime.datetime.now().timestamp() + token_info['expires_in']

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

    if datetime.datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')

    return "Thank you for logging in, you may close this window now!\n DEBUG ACCESS_TOKEN: " + session['access_token']


# END OF FLASK APP, FUNCS START HERE


def search_for_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = {"Authorization": "Bearer " + token}
    query = f"?q={artist_name}&type=artist&limit=1"
    query_url = url+query
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

def search_for_album(token, album_name):
    url = "https://api.spotify.com/v1/search"
    headers = {"Authorization": "Bearer " + token}
    query = f"?q={album_name}&type=album&limit=1"
    query_url = url+query
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


def prev(access_token):
    headers = {
        'Authorization': f"Bearer {access_token}"
    }
    response = requests.post(API_BASE_URL + 'me/player/previous', headers=headers)
    return response


def pause(access_token):
    headers = {
        'Authorization': f"Bearer {access_token}"
    }
    response = requests.put(API_BASE_URL + 'me/player/pause', headers=headers)
    return response


def play(access_token):
    headers = {
        'Authorization': f"Bearer {access_token}"
    }
    response = requests.put(API_BASE_URL + 'me/player/play', headers=headers)
    return response


def search_for_song(token, song_name):
    url = "https://api.spotify.com/v1/search"
    headers = {"Authorization": "Bearer " + token}
    query = f"?q={song_name}&type=track&limit=1"
    query_url = url+query
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


def increase_volume(access_token):
    currentstate = get_playback_state(access_token)
    vol = currentstate['device']['volume_percent']
    print(vol)
    vol = vol+15
    if vol > 100:
        vol = 100
    headers = {'Authorization': f"Bearer {access_token}"}
    url = API_BASE_URL + f"me/player/volume?volume_percent={vol}"
    response = requests.put(url, headers=headers)
    return response


def decrease_volume(access_token):
    currentstate = get_playback_state(access_token)
    vol = currentstate['device']['volume_percent']
    if vol > 20:
        vol = vol-15
    else:
        vol = vol/2
    headers = {'Authorization': f"Bearer {access_token}"}
    url = API_BASE_URL + f"me/player/volume?volume_percent={vol}"
    response = requests.put(url, headers=headers)
    return response


def set_volume_to(access_token, vol):   # Takes user access token and desired volume in percent (0-100 including)
    headers = {'Authorization': f"Bearer {access_token}"}
    url = API_BASE_URL + f"me/player/volume?volume_percent={vol}"
    response = requests.put(url, headers=headers)
    return response


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


def turn_on_shuffle(access_token):
    headers = {'Authorization': f"Bearer {access_token}"}
    response = requests.put(API_BASE_URL+'me/player/shuffle?state=true', headers=headers)
    return response


def turn_off_shuffle(access_token):
    headers = {'Authorization': f"Bearer {access_token}"}
    response = requests.put(API_BASE_URL+'me/player/shuffle?state=false', headers=headers)
    return response


#print(search_for_artist(get_token(), "joy division"))
#print(play_artist(acc, "joy divison").content)
#print(play_album(acc, "").content)
#print(play_song(acc, "disorder").content)
#set_volume_to(acc, 100)
#print(turn_off_shuffle(acc).content)
#open_login_flask_app()
#print(get_playlists(acc))