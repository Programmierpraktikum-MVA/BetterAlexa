import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth

class SpotifyPlayer:
    def __init__(self):
        # Replace these with your own Spotify client ID, secret, and redirect URI
        self.spotify_client_id = os.getenv("SPOTIFY_CLIENT_ID")
        self.spotify_client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
        self.spotify_redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI")

        # Scopes for searching and playing music
        scope = "user-read-private user-modify-playback-state user-read-playback-state"

        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope,
                                                       client_id=self.spotify_client_id,
                                                       client_secret=self.spotify_client_secret,
                                                       redirect_uri=self.spotify_redirect_uri))
        # Get the user's available devices
        devices = self.sp.devices()
        self.device_id = devices['devices'][0]['id']  # assuming the first device is the one we want

    def play_song(self, song_name):
        # Search for the song
        results = self.sp.search(q=song_name, limit=1, type='track')

        # Get the first song from the search results
        song_uri = results['tracks']['items'][0]['uri']

        # Start playback
        self.sp.start_playback(device_id=self.device_id, uris=[song_uri])

    def play_artist(self, artist_name):
        # Search for the artist
        results = self.sp.search(q=artist_name, limit=1, type='artist')

        # Get the first artist from the search results
        artist_uri = results['artists']['items'][0]['uri']

        # Start playback
        self.sp.start_playback(device_id=self.device_id, context_uri=artist_uri)

    def play_album(self, album_name):
        # Search for the album
        results = self.sp.search(q=album_name, limit=1, type='album')

        # Get the first album from the search results
        album_uri = results['albums']['items'][0]['uri']

        # Start playback
        self.sp.start_playback(device_id=self.device_id, context_uri=album_uri)

    def play_playlist(self, playlist_name):
        # Search for the playlist
        results = self.sp.search(q=playlist_name, limit=1, type='playlist')

        # Get the first playlist from the search results
        playlist_uri = results['playlists']['items'][0]['uri']

        # Start playback
        self.sp.start_playback(device_id=self.device_id, context_uri=playlist_uri)
