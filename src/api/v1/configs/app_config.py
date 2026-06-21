from dotenv import find_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=find_dotenv(),
        case_sensitive=False,
        extra="ignore",
    )

    DEBUG: bool = False
    HOST: str = "localhost"
    PORT: int = 8000
    TITLE: str = "Linguo API"


app_config = BaseConfig() # type: ignore
