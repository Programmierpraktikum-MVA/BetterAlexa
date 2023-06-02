from flask import Flask, stream_with_context, Response, request
import repo

PORT = 58585
REPO_URL = "https://github.com/Programmierpraktikum-MVA/BetterAlexa.git"
PRODUCTION_PATH = "~/production"
DEVELOPMENT_PATH = "~/development"

app = Flask(__name__)

@app.get("/deploy_production")
def deploy_production():
    def responseStream():    
        yield "Deploying to production\n"
        yield "Getting latest changes\n"
        
        try:
            repo.setup_repo(
                remote_url=REPO_URL,
                path=PRODUCTION_PATH,
                branch="main"
            )
        except Exception as e:
            yield f"Error while pulling latest changes: {e}\n"
            return
        
        yield "Successfully pulled latest changes\n"
        # Todo delete build, install dependencies, prod secrets, build, start server
        yield "Deployment complete\n"
    return Response(stream_with_context(responseStream()))

@app.get("/deploy_development")
def deploy_production():
    def responseStream():    
        yield "Deploying to development\n"
        yield "Getting latest changes\n"
        
        try:
            repo.setup_repo(
                remote_url=REPO_URL,
                path=DEVELOPMENT_PATH,
                branch="develop"
            )
        except Exception as e:
            yield f"Error while pulling latest changes: {e}\n"
            return
        
        yield "Successfully pulled latest changes\n"
        # Todo delete build, install dependencies, dev secrets, build, start server
        yield "Deployment complete\n"
    return Response(stream_with_context(responseStream()))

if __name__ == "__main__":
    app.run(port=PORT)