import spotipy
import os


class SpotifyPlayer:
    def __init__(self, auth):
        self.auth = auth
        self.sp = spotipy.Spotify(self.auth)
        # Get the user's available devices
        try:
            self.devices = self.sp.devices()
        except Exception as e:
            if str(e).find("The access token expired") != -1:
                base_url = os.environ.get("NEXT_PUBLIC_BASE_URL")
                raise Exception(
                    f"Your Spotify access token has expired. Please reauthenticate at {base_url}/spotify."
                )
            elif str(e).find("Invalid access token") != -1:
                base_url = os.environ.get("NEXT_PUBLIC_BASE_URL")
                raise Exception(
                    f"Invalid spotify access token, please go to {base_url}/spotify to reauthenticate."
                )
            raise Exception("Can't get devices list: " + str(e))

        # assuming the first device is the one we want
        try:
            self.device_id = self.devices["devices"][0]["id"]
            if not self.device_id:
                raise Exception(
                    "No device found, please make sure you have one connected"
                )
        except Exception as e:
            raise Exception("Can't get device id: " + str(e))

    def play_song_from_artist(self, song_name, artist_name):
        # Search for the song
        results = self.sp.search(
            q=f"track:{song_name} artist:{artist_name}", limit=1, type="track"
        )

        # Get the first song from the search results
        song_uri = results["tracks"]["items"][0]["uri"]

        # Start playback
        self.sp.start_playback(device_id=self.device_id, uris=[song_uri])
        return results["tracks"]["items"][0]

    def play_song(self, song_name):
        # Search for the song
        results = self.sp.search(q=song_name, limit=1, type="track")

        # Get the first song from the search results
        song_uri = results["tracks"]["items"][0]["uri"]

        # Start playback
        self.sp.start_playback(device_id=self.device_id, uris=[song_uri])
        return results["tracks"]["items"][0]

    def play_artist(self, artist_name):
        # Search for the artist
        results = self.sp.search(q=artist_name, limit=1, type="artist")

        # Get the first artist from the search results
        artist_uri = results["artists"]["items"][0]["uri"]

        # Start playback
        self.sp.start_playback(device_id=self.device_id, context_uri=artist_uri)
        return results["artists"]["items"][0]

    def play_album_from_artist(self, album_name, artist_name):
        # Search for the album
        results = self.sp.search(
            q=f"{album_name} artist:{artist_name}", limit=1, type="album"
        )

        # Get the first album from the search results
        album_uri = results["albums"]["items"][0]["uri"]

        # Start playback
        self.sp.start_playback(device_id=self.device_id, context_uri=album_uri)
        return results["albums"]["items"][0]

    def play_album(self, album_name):
        # Search for the album
        results = self.sp.search(q=album_name, limit=1, type="album")

        # Get the first album from the search results
        album_uri = results["albums"]["items"][0]["uri"]

        # Start playback
        self.sp.start_playback(device_id=self.device_id, context_uri=album_uri)
        return results["albums"]["items"][0]

    def play_playlist(self, playlist_name):
        # Search for the playlist
        results = self.sp.search(q=playlist_name, limit=1, type="playlist")

        # Get the first playlist from the search results
        playlist_uri = results["playlists"]["items"][0]["uri"]

        # Start playback
        self.sp.start_playback(device_id=self.device_id, context_uri=playlist_uri)
        return results["playlists"]["items"][0]
