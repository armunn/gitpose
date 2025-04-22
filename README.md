# gitpose

This is a Python-based GitOps tool named **gitpose**, designed to manage Docker Compose deployments based on changes in a Git repository.

## Features
- Pulls a Git repository and processes deployments based on the `DEPLOYMENT_HOSTNAME` environment variable.
- Supports three modes of operation:
  1. **Run Once**: Executes the deployment process once.
  2. **Polling**: Periodically checks the Git repository for changes and triggers deployments.
  3. **Webhook**: Listens for webhook events to trigger deployments.

## Prerequisites
- Docker and Docker Compose installed on the host machine.
- A private SSH key for accessing the Git repository.

## Environment Variables
- `GIT_REPO`: URL of the Git repository.
- `DEPLOYMENT_HOSTNAME`: Hostname to determine the deployment folder.
- `MODE`: Operation mode (`run_once`, `polling`, or `webhook`).
- `PRIVATE_KEY_PATH`: Path to the private SSH key.
- `POLL_INTERVAL`: (Optional) Polling interval in seconds (default: 60).
- `WEBHOOK_PORT`: (Optional) Port for webhook mode (default: 5000).

## Usage

### Build and Run with Docker Compose
1. Clone this repository.
2. Create a `.env` file with the required environment variables:
   ```env
   GIT_REPO=git@github.com:your/repo.git
   DEPLOYMENT_HOSTNAME=your-hostname
   MODE=run_once
   PRIVATE_KEY_PATH=/path/to/your/private/key
   POLL_INTERVAL=60
   WEBHOOK_PORT=5000
   ```
3. Run the following command to build and start the container:
   ```bash
   docker-compose up --build
   ```

### Modes of Operation
- **Run Once**: Executes the deployment process once and exits.
- **Polling**: Continuously polls the Git repository for changes.
- **Webhook**: Starts a Flask server to listen for webhook events.

## License
This project is licensed under the MIT License.