# MediaVault

MediaVault is a Vue web client with a Python/aiohttp backend that resolves and
proxies YouTube media. The production Docker image contains both the built web
application and the backend.

## Local development

Requirements:

- Node.js 22
- Python 3.14
- [uv](https://docs.astral.sh/uv/)

Create the server configuration:

```sh
cp server/.env.example server/.env
```

Install and run the backend:

```sh
cd server
UV_PROJECT_ENVIRONMENT=../.venv uv sync
UV_PROJECT_ENVIRONMENT=../.venv uv run python main.py
```

Install and run the frontend in another terminal:

```sh
cd app
npm ci
npm run serve
```

Local HTTPS certificates are optional. Put them in `app/certs/` and set
`VUE_APP_LOCAL_HTTPS=true` when starting the development server. Certificates,
private keys and `.env` files are excluded from Git and from the Docker build.

## Checks

```sh
npm ci --prefix app
npm run lint --prefix app
npm run build --prefix app
cd server && UV_PROJECT_ENVIRONMENT=../.venv uv run python -m unittest discover -s tests -v
```

## Docker

Build and start locally:

```sh
docker build -t mediavault:local .
DOCKER_IMAGE=mediavault IMAGE_TAG=local docker compose up -d
```

The application is available at `http://localhost:8090`. Override the public
port with `PUBLIC_PORT`.

## Automated deployment

The workflow `.github/workflows/ci-pr.yml` builds and tests the production
container for every non-`master` push. After CI succeeds, it creates, merges and
closes a pull request into `master`, then deletes the source branch.

The workflow `.github/workflows/deploy.yml` runs only for `master`, publishes a
versioned and `latest` image to Docker Hub, copies `docker-compose.yml` to the
VPS, pulls the versioned image and starts it with Docker Compose.

Create a GitHub Environment named `deploy`, then add these environment secrets:

| Secret | Value |
| --- | --- |
| `AUTOMATION_TOKEN` | Fine-grained PAT allowed to create/merge PRs, delete branches and trigger workflows |
| `DOCKERHUB_USERNAME` | Docker Hub username |
| `DOCKERHUB_TOKEN` | Docker Hub access token with push/pull access |
| `DEPLOY_HOST` | VPS hostname or IP address |
| `DEPLOY_PORT` | SSH port; use `22` when unchanged |
| `DEPLOY_USER` | SSH user allowed to run Docker |
| `DEPLOY_SSH_KEY` | Private SSH key for that user |
| `DEPLOY_PATH` | Existing absolute deployment directory, for example `/opt/mediavault` |
| `DEPLOY_ENV_FILE` | Optional application environment values written to the VPS `.env` |

Optionally set repository variable `DOCKER_IMAGE_NAME`; it defaults to
`mediavault`.

The VPS must have Docker Engine with the Compose plugin installed. Create
`DEPLOY_PATH` before the first run. The SSH user must be able to write there and
use Docker without an interactive `sudo` prompt. Add the public half of
`DEPLOY_SSH_KEY` to the user's `~/.ssh/authorized_keys`.

The branch workflow is:

1. Push development commits to any branch except `master`.
2. GitHub Actions builds the production image and runs tests inside it.
3. After successful checks, the workflow creates or reuses a PR into `master`.
4. The workflow merges the PR with `AUTOMATION_TOKEN` and deletes its branch.
5. The resulting push to `master` publishes the image and deploys it to the VPS.

Manual workflow dispatch deploys only when it is started from `master`.

If the `deploy` environment has required reviewers, both automatic PR merging
and deployment will wait for environment approval. Do not add required reviewers
if the flow must be completely automatic.
