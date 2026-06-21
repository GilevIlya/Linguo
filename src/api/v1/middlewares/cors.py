import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

def register_cors_middleware(app: FastAPI) -> None:
    origins = os.getenv("CORS_ORIGINS", "")
    origin_list = origins.split(",") if origins else []

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )