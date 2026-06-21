import logging
import uuid

import pytest
from aioboto3 import Session  # type: ignore
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine
from sqlalchemy.pool import NullPool
from testcontainers.minio import MinioContainer
from testcontainers.postgres import PostgresContainer

from api.v1.configs.s3_config import s3_config
from api.v1.models import User
from api.v1.repositories.user_repository import UserRepository
from api.v1.services.file_service import FileService
from api.v1.services.s3_service import S3Service
from api.v1.services.user_service import UserService
from src.api.v1.models.basemodel import BaseModel as Base
from src.main import get_app


@pytest.fixture(autouse=True, scope="session")
def mute_sqlalchemy_logs():
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

app = get_app()

@pytest.fixture(scope="session")
def minio_container():
    with MinioContainer() as container:
        yield container

@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:17", driver="asyncpg") as postgres:
        yield postgres

@pytest.fixture(scope="session")
def engine(postgres_container: PostgresContainer):
    url = postgres_container.get_connection_url()
    url = url.replace("postgresql://", "postgresql+asyncpg://")

    engine = create_async_engine(
        url,
        poolclass=NullPool,
    )

    yield engine

@pytest.fixture(scope="session", autouse=True)
async def create_tables(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@pytest.fixture
async def session(engine: AsyncEngine):
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        yield session
        await session.rollback()

@pytest.fixture()
async def user_service(session):
    from api.v1.repositories.user_repository import UserRepository
    return UserService(UserRepository(session))

@pytest.fixture()
async def feedback_service(session, user_service):
    from api.v1.repositories.FeedbackRepository import FeedbackRepository
    from api.v1.services.FeedbackService import FeedbackService
    return FeedbackService(FeedbackRepository(session), user_service)

@pytest.fixture(scope="session")
def s3_session(minio_container):
    return Session()

@pytest.fixture(scope="session")
async def s3_service(minio_container, s3_session):
    host = minio_container.get_container_host_ip()
    port = minio_container.get_exposed_port(9000)

    s3_config.S3_ENDPOINT = f"http://{host}:{port}"
    s3_config.S3_ACCESS_KEY = minio_container.access_key
    s3_config.S3_SECRET_KEY = minio_container.secret_key
    s3_config.S3_BUCKET_NAME = "test-bucket"
    s3_config.S3_REGION = "us-east-1"
    s3_config.S3_USE_SSL = False

    service = S3Service(s3_session)
    async with service._get_client() as client:
        await client.create_bucket(Bucket="test-bucket")
    return service

@pytest.fixture()
async def file_service(session, s3_service):
    from api.v1.repositories.file_repository import FileRepository
    return FileService(s3_service, FileRepository(session))

@pytest.fixture()
async def user_repository(session):
    return UserRepository(session)

@pytest.fixture
def create_user():
    def _make():
        uid = uuid.uuid4().hex[:8]
        return User(
            id=uuid.uuid4(),
            email=f"user_{uid}@test.com",
            password="hashed"
        )
    return _make

@pytest.fixture
async def new_user(user_service: UserService, create_user):
    user = create_user()
    return await user_service.create_user(user)