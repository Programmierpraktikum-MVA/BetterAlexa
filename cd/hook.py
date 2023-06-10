from flask import Flask, stream_with_context, Response
import docker
import repo
import os

PORT = 58585
REPO_URL = "https://github.com/Programmierpraktikum-MVA/BetterAlexa.git"
HOME_PATH = os.path.expanduser("~")
REPO_PATH = f"{HOME_PATH}/repo"
PRODUCTION_PATH = f"{HOME_PATH}/production"
DEVELOPMENT_PATH = f"{HOME_PATH}/development"

app = Flask("betteralexa-CD-hook")

@app.get("/deploy_production")
def deploy_production():
    def responseStream():    
        yield "Deploying to production\n"
        yield "Getting latest changes\n"
        
        try:
            repo.setup_repo(
                remote_url=REPO_URL,
                path=REPO_PATH,
                branch="main"
            )
        except Exception as e:
            yield f"Error while pulling latest changes: {e}\n"
            return
        
        yield "Successfully pulled latest changes\n"

        if os.path.exists(PRODUCTION_PATH):
            yield "Stopping old server\n"
            # Todo stop old server
            yield "Deleting old build\n"
            # Todo delete old build
            
        yield "Installing dependencies\n"
        # Todo install dependencies
        
        yield "Applying production secrets/vars\n"
        # Todo apply production secrets/vars
        
        yield "Building\n"
        # Todo build
        
        yield "Starting server\n"
        # Todo start server
        
        yield "Deployment complete\n"
    return Response(stream_with_context(responseStream()))

@app.get("/deploy_development")
def deploy_development():
    def responseStream():    
        yield "Deploying to development\n"
        yield "Getting latest changes\n"
        
        try:
            repo.setup_repo(
                remote_url=REPO_URL,
                path=REPO_PATH,
                branch="develop"
            )
        except Exception as e:
            yield f"Error while pulling latest changes: {e}\n"
            return
        
        yield "Successfully pulled latest changes\n"
        
        if os.path.exists(PRODUCTION_PATH):
            yield "Stopping old server\n"
            # Todo stop old server
            yield "Deleting old build\n"
            # Todo delete old build
            
        yield "Installing dependencies\n"
        # Todo install dependencies
        
        yield "Applying production secrets/vars\n"
        # Todo apply production secrets/vars
        
        yield "Building\n"
        # Todo build
        
        yield "Starting server\n"
        # Todo start server
        
        yield "Deployment complete\n"
    return Response(stream_with_context(responseStream()))

if __name__ == "__main__":
    app.run(port=PORT, host="0.0.0.0")