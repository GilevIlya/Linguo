from functools import lru_cache

from dotenv import find_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


class ExternalAPIConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=find_dotenv(),
        case_sensitive=False,
        extra="ignore",
    )

    EXTERNAL_API_BASE_URL: str = "https://api.example.com"
    EXTERNAL_API_TIMEOUT: float = 30.0
    EXTERNAL_API_RETRY_ATTEMPTS: int = 3
    EXTERNAL_API_RETRY_DELAY: float = 1.0


@lru_cache
def get_external_api_config() -> ExternalAPIConfig:
    return ExternalAPIConfig()