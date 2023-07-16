from flask import Flask, request
from waitress import serve
import sys
import openai
import json
import os
from spotify import SpotifyPlayer

app = Flask(__name__)
app.logger.setLevel("INFO")

functions = [
    {
        "name": "spotify_player",
        "description": "Plays a song, artist, album, or playlist on Spotify.",
        "parameters": {
            "type": "object",
            "properties": {
                "song_title": {
                    "type": "string",
                    "description": "The title of the song to play.",
                },
                "artist_name": {
                    "type": "string",
                    "description": "The name of the artist to play.",
                },
                "album_name": {
                    "type": "string",
                    "description": "The name of the album to play.",
                },
                "playlist_name": {
                    "type": "string",
                    "description": "The name of the playlist to play.",
                },
            },
        },
    }
]


def spotify_player(args, token):
    try:
        spotify_player = SpotifyPlayer(token)
        if args.get("song_title") and args.get("artist_name"):
            song_title = args["song_title"]
            artist_name = args["artist_name"]
            spotify_player.play_song_from_artist(song_title, artist_name)
            return f"Playing {song_title} by {artist_name} on Spotify."
        elif args.get("song_title"):
            song_title = args["song_title"]
            spotify_player.play_song(song_title)
            return f"Playing {song_title} on Spotify."
        elif args.get("artist_name"):
            artist_name = args["artist_name"]
            spotify_player.play_artist(artist_name)
            return f"Playing {artist_name} on Spotify."
        elif args.get("album_name"):
            album_name = args["album_name"]
            spotify_player.play_album(album_name)
            return f"Playing {album_name} on Spotify."
        elif args.get("playlist_name"):
            playlist_name = args["playlist_name"]
            spotify_player.play_playlist(playlist_name)
            return f"Playing {playlist_name} on Spotify."
        else:
            return "You need to specify a song, artist, album, or playlist to play on Spotify."
    except Exception as e:
        return f"Error: {e}"


@app.route("/")
def home():
    return {"message": "Hello, World!"}


@app.route("/command-to-action", methods=["POST"])
def generate_cta():
    try:
        # Check if request method is POST
        if request.method != "POST":
            return "Method Not Allowed", 405

        # Parse incoming data as binary
        data = request.get_data()
        text = data.decode("utf-8")
        messages = [{"role": "user", "content": text}]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            messages=messages,
            functions=functions,
            function_call="auto",
        )
        response_message = response["choices"][0]["message"]
        app.logger.info(f"Response message: {response_message}")

        if response_message.get("function_call"):
            function_call = response_message["function_call"]
            function_name = function_call["name"]
            arguments = json.loads(function_call["arguments"])
            if function_name == "spotify_player":
                if request.headers.get("x-spotify-access-token"):
                    access_token = request.headers["x-spotify-access-token"]
                    response_text = spotify_player(arguments, access_token)
                else:
                    base_url = os.environ.get("NEXT_PUBLIC_BASE_URL")
                    response_text = f"You need to authenticate with Spotify first. Go to {base_url}/spotify to do so."
            else:
                response_text = "I don't know how to do that yet."
        else:
            response_text = response_message["content"]

        result = {
            "text": response_text,
        }

        # Respond with success message
        return {"result": result}, 200
    except Exception as e:
        app.logger.error(f"Command to action error: {e}")
        return {"error": "Internal Server Error"}, 500


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "dev":
        app.run(host="::", port=3002, debug=True)
    else:
        app.logger.info(" * Running command to action production server on port 3002")
        serve(app, host="0.0.0.0", port=3002)
