from functools import lru_cache

from aioboto3 import Session  # type: ignore[import-untyped]
from dotenv import find_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


class S3Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=find_dotenv(),
        case_sensitive=False,
        extra="ignore",
    )
    S3_ENDPOINT: str = "s3:9000"
    S3_ACCESS_KEY: str = "S3accesskey"
    S3_SECRET_KEY: str = "S3secretkey"
    S3_BUCKET_NAME: str = "linguo-data"
    S3_USE_SSL: bool = False
    S3_REGION: str = "us-east-1"

s3_config = S3Config()

@lru_cache
def get_s3_session() -> Session:
    return Session()
