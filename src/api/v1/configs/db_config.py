from dotenv import find_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from .app_config import app_config


class PostgresConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=find_dotenv(),
        case_sensitive=False,
        extra="ignore",
    )

    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "linguo_db"

    @property
    def POSTGRES_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

postgres_config = PostgresConfig() # type: ignore

engine = create_async_engine(url=postgres_config.POSTGRES_URL, echo=app_config.DEBUG)

session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)


async def get_session(): # TODO: вынести в отдельный класс
    async with session_factory() as session:
        yield session
