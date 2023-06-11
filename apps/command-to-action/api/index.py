from flask import Flask, request
import os

from langchain_integration import LangChainIntegration

app = Flask(__name__)

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
        text = data.decode("utf-8")
        response = langchainIntegration.agent_executor.run(input=text)
        result = {
            "text": response,
        }

        # Respond with success message
        return {"result": result}, 200
    except Exception as e:
        print(e)
        return {"error": "Internal Server Error"}, 500


if __name__ == "__main__":
    app.run(host="::", port=3001, debug=os.environ.get("DEBUG", False))
