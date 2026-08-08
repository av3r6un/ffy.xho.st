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
- Web Push notifications when asynchronously prepared videos become ready
- An Apple Shortcut that submits shared YouTube URLs without opening the browser
- Responsive interface with Safari support

## PWA notifications

MediaVault uses the Notifications API to display notifications and the Push API to receive them while the PWA is in the background or closed. The browser creates a push subscription, the backend stores it for the authenticated user, and `pywebpush` sends an encrypted payload through the browser vendor's push service.

### 1. Requirements

- The production site must use HTTPS.
- A service worker must control the application.
- The user must grant notification permission from a user action such as a button click.
- On iPhone and iPad, Web Push is available only to a website installed on the Home Screen.
- The VAPID key pair must remain stable. Replacing it requires browsers to create new subscriptions.

`localhost` is treated as a secure context for local development. A different device cannot use the development machine's `localhost`; expose the development server through HTTPS when testing on a phone or tablet.

### 2. Generate VAPID keys

Install the backend dependencies, then generate an environment-ready key pair:

```sh
cd server
uv sync
.venv/bin/python - <<'PY'
import base64
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from py_vapid import Vapid

encode = lambda value: base64.urlsafe_b64encode(value).rstrip(b'=').decode()
vapid = Vapid()
vapid.generate_keys()
private_value = vapid.private_key.private_numbers().private_value.to_bytes(32, 'big')
public_value = vapid.public_key.public_bytes(Encoding.X962, PublicFormat.UncompressedPoint)
print(f'VAPID_PUBLIC_KEY={encode(public_value)}')
print(f'VAPID_PRIVATE_KEY={encode(private_value)}')
PY
```

Copy both generated values and configure the contact subject expected by `pywebpush`:

```dotenv
VAPID_PUBLIC_KEY=<generated public key>
VAPID_PRIVATE_KEY=<generated private key>
VAPID_SUBJECT=mailto:admin@example.com
```

`VAPID_SUBJECT` must be a `mailto:` address or an HTTPS URL. Never expose `VAPID_PRIVATE_KEY` to the frontend or commit it to the repository.

### 3. Pass the variables to production

Defining values in a host `.env` file does not automatically place them inside a container when Compose has an explicit `environment` section. Pass all three variables:

```yaml
services:
  mediavault:
    environment:
      VAPID_PUBLIC_KEY: "${VAPID_PUBLIC_KEY:?Set VAPID_PUBLIC_KEY}"
      VAPID_PRIVATE_KEY: "${VAPID_PRIVATE_KEY:?Set VAPID_PRIVATE_KEY}"
      VAPID_SUBJECT: "${VAPID_SUBJECT:?Set VAPID_SUBJECT}"
```

Verify their presence without printing the secrets:

```sh
docker exec mediavault sh -c '
  test -n "$VAPID_PUBLIC_KEY" && echo public:set || echo public:missing
  test -n "$VAPID_PRIVATE_KEY" && echo private:set || echo private:missing
  test -n "$VAPID_SUBJECT" && echo subject:set || echo subject:missing
'
```

### 4. Browser subscription flow

1. The UI calls `Notification.requestPermission()` from the Subscribe button.
2. The frontend waits for `navigator.serviceWorker.ready`.
3. It requests `GET /api/push/vapid-public-key`.
4. `PushManager.subscribe()` creates a browser subscription using the public VAPID key.
5. The frontend sends its `endpoint`, `p256dh`, and `auth` values to `POST /api/push/subscriptions`.
6. The backend associates the subscription with the authenticated user.

The permission and push subscription are separate browser states. Permission can be `granted` while no usable subscription exists, so the application always checks or recreates the subscription.

To unsubscribe, the frontend calls `DELETE /api/push/subscriptions` and then removes the browser subscription through `PushSubscription.unsubscribe()`.

### 5. Sending notifications

Video metadata preparation runs asynchronously. When a session becomes ready or fails, the backend:

1. loads every active subscription belonging to the session owner;
2. creates a payload in the user's saved language;
3. sends it outside the event loop through `pywebpush`;
4. retries temporary HTTP `429` and `5xx` failures;
5. revokes subscriptions rejected with HTTP `404` or `410`.

The service worker handles the `push` event and calls `showNotification()`. The payload contains a URL such as `/#/watch?session=<uid>`. Clicking it opens the PWA or navigates the existing PWA window. The Watch view observes the route's `session` query parameter, tears down the previous player, and loads the selected session without requiring a page reload.

### 6. Service workers in development and production

Production uses `app/src/service-worker.js`, built with Workbox InjectManifest. Development uses `app/public/service-worker.dev.js` because Vue CLI normally registers its PWA service worker only for production builds.

After changing service-worker code, close all installed PWA windows or unregister the old worker before retesting. Otherwise the browser may continue running an earlier cached version.

### 7. Testing and diagnostics

With backend `DEBUG=1`, opening the permission modal can send a test notification. Test delivery is also available through `POST /api/push/test` for a registered endpoint.

The expected server request sequence is:

```text
GET  /api/push/vapid-public-key
POST /api/push/subscriptions
POST /api/push/test              # development test only
```

If only the public-key request appears, inspect its JSON body and confirm that `public_key` is not `null`. The failure happened in the browser before subscription storage, commonly because of a missing VAPID key, denied permission, an inactive service worker, or an insecure context.

When `DEBUG=1`, the exact response envelope for `POST /shortcut/sessions` is written to the regular application log:

```text
Shortcut response HTTP 200: {'status': 'success', 'body': {...}}
```

This is useful when updating the Apple Shortcut without changing the shared response middleware. Authorization headers and raw Shortcut tokens are never logged.

### 8. Apple Shortcut integration

The PWA creates a personal Shortcut token through `POST /api/shortcuts`, copies it to the clipboard, and opens the shared iCloud Shortcut. The token is entered once during installation and is stored in that installed Shortcut. The backend stores only its SHA-256 hash.

The Shortcut sends:

```http
POST /shortcut/sessions
Authorization: Bearer <shortcut-token>
Content-Type: application/json

{"video_url":"<shared YouTube URL>"}
```

The route authenticates the token, creates or reuses a video session, and returns the standard API response envelope. The Shortcut should inspect the actual logged response before configuring its conditions. Once preparation finishes, Web Push delivers the final result and opens the corresponding session when tapped.

Use `DELETE /api/shortcuts/{id}` to revoke an installed Shortcut token. Creating another token does not revoke existing devices.

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
