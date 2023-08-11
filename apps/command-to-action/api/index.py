from flask import Flask, request
from waitress import serve
import sys
import openai
import json
import os

from spotify import SpotifyPlayer

# uncomment to allow langchain integration
# from langchain_integration import LangChainIntegration

app = Flask(__name__)
app.logger.setLevel("INFO")

# uncomment to allow langchain integration
# langchainIntegration = LangChainIntegration()

def generate_response_from_openai_functions(text):
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
    messages = [{"role": "user", "content": text}]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=messages,
        functions=functions,
        function_call="auto",
    )
    response_message = response["choices"][0]["message"]
    
    return response_message
# uncomment to use langchain integration
# def generate_response_from_langchain(text):
#     langchainIntegration.spotify_auth = request.headers.get("x-spotify-access-token")
#     response = langchainIntegration.agent_executor.run(input=text)
#     return response


def spotify_player(args, token):
    try:
        spotify_player = SpotifyPlayer(token)
        if args.get("song_title") and args.get("artist_name"):
            spotify_result = spotify_player.play_song_from_artist(
                args["song_title"], args["artist_name"]
            )
            song_title = spotify_result["name"]
            artist_name = spotify_result["artists"][0]["name"]
            return f"Playing {song_title} by {artist_name} on Spotify."
        elif args.get("album_name") and args.get("artist_name"):
            spotify_result = spotify_player.play_album_from_artist(
                args["album_name"], args["artist_name"]
            )
            album_name = spotify_result["name"]
            artist_name = spotify_result["artists"][0]["name"]
            return f"Playing Album {album_name} by {artist_name} on Spotify."
        elif args.get("song_title"):
            spotify_result = spotify_player.play_song(args["song_title"])
            song_title = spotify_result["name"]
            artist_name = spotify_result["artists"][0]["name"]
            return f"Playing {song_title} by {artist_name} on Spotify."
        elif args.get("artist_name"):
            spotify_result = spotify_player.play_artist(args["artist_name"])
            artist_name = spotify_result["name"]
            return f"Playing songs by {artist_name} on Spotify."
        elif args.get("album_name"):
            spotify_result = spotify_player.play_album(args["album_name"])
            album_name = spotify_result["name"]
            artist_name = spotify_result["artists"][0]["name"]
            return f"Playing {album_name} by {artist_name} on Spotify."
        elif args.get("playlist_name"):
            spotify_result = spotify_player.play_playlist(args["playlist_name"])
            playlist_name = spotify_result["name"]
            owner_name = spotify_result["owner"]["display_name"]
            return f"Playing Playlist {playlist_name} by {owner_name} on Spotify."
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
        if request.method != "POST":
            return "Method Not Allowed", 405

        data = request.get_data()
        text = data.decode("utf-8")
        response_message = generate_response_from_openai_functions(text)
        # swrap to use langchain
        # response_message = generate_response_from_langchain(text)

        if response_message.get("function_call"):
            function_call = response_message["function_call"]
            function_name = function_call["name"]
            arguments = json.loads(function_call["arguments"])
            if function_name == "spotify_player":
                access_token = request.headers.get("x-spotify-access-token")
                if access_token and access_token != "undefined":
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
