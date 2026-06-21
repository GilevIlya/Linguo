from unittest.mock import AsyncMock

import pytest

from api.v1.repositories.interfaces.ITokenRepository import ITokenRepository
from api.v1.services.tokens_service import TokenService


@pytest.fixture
def token_repository() -> AsyncMock:
    return AsyncMock(spec=ITokenRepository)


@pytest.fixture
def token_svc(token_repository: AsyncMock) -> TokenService:
    return TokenService(token_repository=token_repository)

