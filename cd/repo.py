from git import Repo
import os
import shutil

def _clone_safely(remote_url, path):
    if not os.path.exists(path):
        repo = Repo.clone_from(remote_url, path)
        return repo
    
    try:
        # raises exception if path is not a git repo
        repo = Repo(path)
        
        remote = repo.remotes.origin
        
        if remote.url != remote_url:
            raise Exception("Remote URL mismatch")

        # pull latest changes
        
    except:
        # setup repo from scratch
        shutil.rmtree(path)
        repo = Repo.clone_from(remote_url, path)
            
    return repo


def setup_repo(remote_url, path, branch):

    repo = _clone_safely(remote_url, path)

    repo.remotes.origin.pull(branch)
    repo.branches[branch].checkout()
    
if __name__ == "__main__":
    
    remote_url = "https://github.com/Programmierpraktikum-MVA/BetterAlexa.git"
        
    PRODUCTION_PATH = "./production"
    DEVELOPMENT_PATH = "./development"
    
    setup_repo(remote_url, production_path, "main")
    