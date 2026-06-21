FROM python:3.12.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
#TODO: // delete the above line and use the below line once the uv image is available on dockerhub

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev

COPY . .

RUN chmod +x commands/start-*.sh

ENTRYPOINT ["/bin/sh", "-c", "./commands/start-${PROFILE}.sh"]
