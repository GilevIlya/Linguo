import logging.config
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI

from api.v1.configs.app_config import app_config
from api.v1.configs.logger_config import logger_config
from api.v1.middlewares.cors import register_cors_middleware
from api.v1.middlewares.exceptions_handler import register_exception_handlers
from api.v1.middlewares.logging_middleware import logging_middleware
from api.v1.routers import router
from api.v1.schemas.responses import ErrorResponse

logging.config.dictConfig(logger_config.CONFIG)
logger = logging.getLogger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    print_welcome_message()
    yield
    logger.info("Shutting down the application...")


def print_welcome_message():
    logger.info(r"""
    Starting the application...


    /$$       /$$
    | $$      |__/
    | $$       /$$ /$$$$$$$   /$$$$$$  /$$   /$$  /$$$$$$
    | $$      | $$| $$__  $$ /$$__  $$| $$  | $$ /$$__  $$
    | $$      | $$| $$  \ $$| $$  \ $$| $$  | $$| $$  \ $$
    | $$      | $$| $$  | $$| $$  | $$| $$  | $$| $$  | $$
    | $$$$$$$$| $$| $$  | $$|  $$$$$$$|  $$$$$$/|  $$$$$$/
    |________/|__/|__/  |__/ \____  $$ \______/  \______/
                             /$$  \ $$
                            |  $$$$$$/
                             \______/

    """)
    logger.info(f"Starting {app_config.TITLE} on {app_config.HOST}:{app_config.PORT}...")


def get_global_responses() -> dict[int | str, dict[str, Any]]:
    return {
        422: {
            "model": ErrorResponse,
            "description": "Request validation error.",
        },
    }


def get_app() -> FastAPI:
    app = FastAPI(
        title=app_config.TITLE,
        lifespan=lifespan,
        responses=get_global_responses(),
    )
    app.middleware("http")(logging_middleware)
    app.add_api_route("/", lambda: {"message": "Welcome to the API!"}, methods=["GET"])
    register_cors_middleware(app)
    register_exception_handlers(app)
    app.include_router(router)

    return app

def get_app_prod() -> FastAPI:
    app = FastAPI(
        title=app_config.TITLE,
        lifespan=lifespan,
        docs_url=None,
        redoc_url=None,
        debug=False,
    )
    app.middleware("http")(logging_middleware)
    app.add_api_route("/", lambda: {"message": "Welcome to the API!"}, methods=["GET"])
    register_cors_middleware(app)
    register_exception_handlers(app)
    app.include_router(router)

    return app

if __name__ == "__main__":
    import uvicorn
    app = get_app()
    uvicorn.run(app, host=app_config.HOST, port=app_config.PORT)
