#!/bin/sh
uv run alembic upgrade head && cd src && uv run python -m uvicorn main:get_app --factory --reload --host "$HOST" --port "$PORT"
