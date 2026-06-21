from unittest.mock import AsyncMock

import pytest

from api.v1.services.auth_service import AuthService
from api.v1.services.tokens_service import TokenService
from api.v1.services.user_service import UserService
from api.v1.services.profile_service import ProfileService


@pytest.fixture
def user_service() -> AsyncMock:
    svc = AsyncMock(spec=UserService)
    return svc


@pytest.fixture
def token_service() -> AsyncMock:
    svc = AsyncMock(spec=TokenService)
    return svc

@pytest.fixture
def profile_service() -> AsyncMock:
    svc = AsyncMock(spec=ProfileService)
    return svc


@pytest.fixture
def auth_service(user_service: AsyncMock, token_service: AsyncMock, profile_service: AsyncMock) -> AuthService:
    return AuthService(user_service=user_service, token_service=token_service, profile_service=profile_service)