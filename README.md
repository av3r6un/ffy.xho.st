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

The workflow `.github/workflows/deploy.yml` runs checks, publishes immutable
commit and `latest` tags to Docker Hub, copies `docker-compose.yml` to the VPS,
pulls the commit-tagged image and starts it with Docker Compose.

Create these GitHub repository secrets:

| Secret | Value |
| --- | --- |
| `DOCKERHUB_USERNAME` | Docker Hub username |
| `DOCKERHUB_TOKEN` | Docker Hub access token with push/pull access |
| `VPS_HOST` | VPS hostname or IP address |
| `VPS_PORT` | SSH port; use `22` when unchanged |
| `VPS_USER` | SSH user allowed to run Docker |
| `VPS_SSH_KEY` | Private SSH key for that user |
| `VPS_KNOWN_HOSTS` | Verified `known_hosts` entry for the VPS |
| `VPS_DEPLOY_PATH` | Absolute deployment directory, for example `/opt/mediavault` |

Optionally set repository variable `DOCKER_IMAGE_NAME`; it defaults to
`mediavault`.

The VPS must have Docker Engine with the Compose plugin installed. The SSH user
must be able to create the deployment directory and use Docker without an
interactive `sudo` prompt. Add the public half of `VPS_SSH_KEY` to the user's
`~/.ssh/authorized_keys`.

Generate `VPS_KNOWN_HOSTS` from a trusted machine and verify the fingerprint
against your hosting provider before saving it:

```sh
ssh-keyscan -p 22 your-vps.example.com
```

The branch workflow is:

1. Push development commits to `changes`.
2. GitHub Actions runs frontend and backend checks.
3. After successful checks, the workflow opens a `changes` → `master` pull
   request if one is not already open.
4. Pull requests targeting `master` run the same checks.
5. A merge or direct push to `master` publishes the Docker image and deploys
   it to the VPS.

Manual workflow dispatch deploys only when it is started from `master`.

In repository **Settings → Actions → General → Workflow permissions**, enable
**Allow GitHub Actions to create and approve pull requests** so the workflow can
open the automatic `changes` → `master` pull request. Protect `master` and
require the `test` job before merging.
