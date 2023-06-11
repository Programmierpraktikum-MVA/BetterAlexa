from flask import Flask, request
from waitress import serve
import sys

from langchain_integration import LangChainIntegration

app = Flask(__name__)
app.logger.setLevel("INFO")

langchainIntegration = LangChainIntegration()

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
        langchainIntegration.spotifyAuth = request.headers.get("x-spotify-access-token")
        text = data.decode("utf-8")
        response = langchainIntegration.agent_executor.run(input=text)
        result = {
            "text": response,
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