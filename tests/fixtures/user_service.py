from unittest.mock import AsyncMock

import pytest

from api.v1.repositories.interfaces.IUserRepository import IUserRepository
from api.v1.services.user_service import UserService


@pytest.fixture
def user_repository() -> AsyncMock:
    return AsyncMock(spec=IUserRepository)


@pytest.fixture
def user_svc(user_repository: AsyncMock) -> UserService:
    return UserService(user_repository=user_repository)

