FROM node:22-alpine AS frontend

WORKDIR /build/app
COPY app/package.json app/package-lock.json ./
RUN npm ci
COPY app/ ./
RUN npm run build

FROM ghcr.io/astral-sh/uv:0.10.8 AS uv

FROM python:3.14-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/mediavault/.venv/bin:$PATH" \
    APP_PORT=8090 \
    GENERAL_CONF=settings.yaml,yt_dlp.yaml \
    DEFAULT_AUDIO_ID=139 \
    MEDIAVAULT_STATIC_DIR=/opt/mediavault/static

WORKDIR /opt/mediavault

COPY --from=uv /uv /uvx /bin/
COPY server/pyproject.toml server/uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY server/ ./
COPY --from=frontend /build/app/dist ./static
COPY entrypoint.sh ./entrypoint.sh

RUN addgroup --system mediavault \
    && adduser --system --ingroup mediavault mediavault \
    && chmod +x /opt/mediavault/entrypoint.sh \
    && chown -R mediavault:mediavault /opt/mediavault

USER mediavault

EXPOSE 8090

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8090/health', timeout=3)"

ENTRYPOINT ["/opt/mediavault/entrypoint.sh"]
