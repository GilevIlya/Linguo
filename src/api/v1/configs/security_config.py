from dotenv import find_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


class SecurityConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=find_dotenv(),
        case_sensitive=False,
        extra="ignore",
    )
    SECRET_KEY: str = "your_secret_key_here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_SEC: int = 60*5

    REFRESH_TOKEN_EXPIRE_SEC: int = 60*60*24*7
    COOKIE_NAME_REFRESH_TOKEN: str = "refresh_token"

security_config = SecurityConfig() # type: ignore
