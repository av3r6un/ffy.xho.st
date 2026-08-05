# MediaVault

## Installation

Requirements: Node.js 22, Python 3.14, and [uv](https://docs.astral.sh/uv/).

```sh
git clone <repository-url>
cd mediavault-app

cp server/.env.example server/.env
```

Add the required settings to `server/.env`:

```dotenv
GENERAL_CONF=settings.yaml
DB_URL=sqlite+aiosqlite:///app.db
PLAYBACK_SECRET=replace-with-at-least-32-random-characters
```

Install the backend, apply migrations, and start the server:

```sh
cd server
UV_PROJECT_ENVIRONMENT=../.venv uv sync
../.venv/bin/alembic -c alembic.ini upgrade head
UV_PROJECT_ENVIRONMENT=../.venv uv run python main.py
```

Start the frontend in another terminal:

```sh
cd app
npm ci
npm run serve
```

Open `http://localhost:3000`. The backend runs at `http://localhost:8090`.

## Features

MediaVault is a Vue 3 PWA with an aiohttp backend for watching YouTube videos without the YouTube interface.

- Authentication through an external auth service
- Temporary user-bound playback sessions
- Asynchronous metadata retrieval and caching with yt-dlp
- Quality selection, chapters, descriptions, and video statistics
- Protected DASH audio and video streaming through the proxy
- Responsive interface with Safari support

## Checks

```sh
npm run lint --prefix app
npm run build --prefix app
cd server && UV_PROJECT_ENVIRONMENT=../.venv uv run python -m unittest discover -s tests -v
```

## Docker

```sh
docker build -t mediavault:local .
DOCKER_IMAGE=mediavault IMAGE_TAG=local PLAYBACK_SECRET=<secret> docker compose up -d
```

The production application runs at `http://localhost:8090`. Docker serves a built frontend without hot reload; use `npm run serve` on port `3000` for development.

## Deployment

CI validates the Docker image and runs the backend tests. Branches other than `master` are checked and merged through an automated pull request. Changes on `master` are published to Docker Hub and deployed to a VPS with Docker Compose.
