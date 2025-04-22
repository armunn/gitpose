import os
import subprocess
import time
from flask import Flask, request
from git import Repo

# Flask app for webhook mode
app = Flask(__name__)

# Environment variables
GIT_REPO = os.getenv("GIT_REPO")
DEPLOYMENT_HOSTNAME = os.getenv("DEPLOYMENT_HOSTNAME")
MODE = os.getenv("MODE", "run_once")
PRIVATE_KEY_PATH = os.getenv("PRIVATE_KEY_PATH", "/gitpose/.ssh/id_rsa")
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", 60))
WEBHOOK_PORT = int(os.getenv("WEBHOOK_PORT", 5000))
# Add GIT_REPO_PATH with a default value
GIT_REPO_PATH = os.getenv("GIT_REPO_PATH", "")

# Ensure required environment variables are set
if not GIT_REPO or not DEPLOYMENT_HOSTNAME or not PRIVATE_KEY_PATH:
    raise ValueError("GIT_REPO, DEPLOYMENT_HOSTNAME, and PRIVATE_KEY_PATH environment variables must be set.")

# Clone or pull the git repository
# Modify sync_repo to return a boolean indicating if the repo has changed
def sync_repo():
    repo_path = "/gitpose/repo"
    if not os.path.exists(repo_path):
        Repo.clone_from(GIT_REPO, repo_path, env={"GIT_SSH_COMMAND": f"ssh -i {PRIVATE_KEY_PATH}"})
        return True  # Repo is new, so it has changed
    else:
        repo = Repo(repo_path)
        old_commit = repo.head.commit.hexsha
        repo.remotes.origin.pull(env={"GIT_SSH_COMMAND": f"ssh -i {PRIVATE_KEY_PATH}"})
        new_commit = repo.head.commit.hexsha
        return old_commit != new_commit  # Return True if the commit hash has changed

# Process deployment directories
# Update process_deployments to handle GIT_REPO_PATH and blank DEPLOYMENT_HOSTNAME
def process_deployments(repo_path):
    target_path = os.path.join(repo_path, GIT_REPO_PATH)
    if DEPLOYMENT_HOSTNAME:
        target_path = os.path.join(target_path, DEPLOYMENT_HOSTNAME)

    if not os.path.exists(target_path):
        raise FileNotFoundError(f"Target folder {target_path} does not exist.")

    for subdir in sorted(os.listdir(target_path)):
        subdir_path = os.path.join(target_path, subdir)
        if os.path.isdir(subdir_path):
            os.chdir(subdir_path)
            if os.path.exists("docker-compose.yml"):
                with open("docker-compose.yml", "r") as f:
                    contents = f.read()
                    if "# GP:Disable" in contents:
                        subprocess.run(["docker-compose", "down"], check=True)

                    if "# GP: AlwaysPull" in contents:
                        subprocess.run(["docker-compose", "pull"], check=True)

            subprocess.run(["docker-compose", "up", "-d", "--remove-orphans"], check=True)


# Run once mode
def run_once():
    repo_path = sync_repo()
    process_deployments(repo_path)

# Polling mode
# Update run_polling to check if the repo has changed before invoking deployments
def run_polling():
    while True:
        if sync_repo():  # Only process deployments if the repo has changed
            process_deployments("/gitpose/repo")
        time.sleep(POLL_INTERVAL)

# Webhook mode
@app.route("/webhook", methods=["POST"])
def webhook():
    run_once()
    return "OK", 200

if __name__ == "__main__":
    if MODE == "run_once":
        run_once()
    elif MODE == "polling":
        run_polling()
    elif MODE == "webhook":
        app.run(host="0.0.0.0", port=WEBHOOK_PORT)
    else:
        raise ValueError("Invalid MODE. Must be one of: run_once, polling, webhook.")