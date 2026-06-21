from dotenv import find_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


class PaginationConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=find_dotenv(),
        case_sensitive=False,
        extra="ignore",
    )
    DEFAULT_PER_PAGE: int = 25
    MAX_PER_PAGE: int = 100
    DEFAULT_PAGE: int = 1


pagination_config = PaginationConfig() # type: ignore
