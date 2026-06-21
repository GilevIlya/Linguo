#!/bin/sh

uv run alembic upgrade head && cd src && uv run python -m gunicorn "main:get_app_prod()" \
  --workers "$APP_WORKERS" \
  --forwarded-allow-ips="$WEB_SERVER" \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind "$HOST":"$PORT"
