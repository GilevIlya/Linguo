from unittest.mock import AsyncMock

import pytest

from api.v1.services.exceptions.base_exceptions import NotFoundException
from api.v1.services.exceptions.error_codes.user_error_codes import UserErrorCodes
from api.v1.services.user_service import UserService
from tests.user_service.helpers import _make_user


class TestGetByEmail:
    async def test_get_by_email_returns_found_user(
        self, user_svc: UserService, user_repository: AsyncMock
    ):
        expected_user = _make_user(email="user@example.com")
        user_repository.find_by_email.return_value = expected_user

        result = await user_svc.get_by_email("user@example.com")

        assert result is expected_user

    async def test_get_by_email_calls_repository_with_correct_email(
        self, user_svc: UserService, user_repository: AsyncMock
    ):
        user_repository.find_by_email.return_value = _make_user()

        await user_svc.get_by_email("Exact.Email@Domain.COM")

        user_repository.find_by_email.assert_awaited_once_with("Exact.Email@Domain.COM")

    async def test_get_by_email_not_found_raises_not_found_exception(
        self, user_svc: UserService, user_repository: AsyncMock
    ):
        user_repository.find_by_email.return_value = None

        with pytest.raises(NotFoundException) as exc_info:
            await user_svc.get_by_email("nonexistent@example.com")

        assert exc_info.value.error_code == UserErrorCodes.USER_NOT_FOUND.value

    async def test_get_by_email_repository_raises_unexpected_exception(
        self, user_svc: UserService, user_repository: AsyncMock
    ):
        user_repository.find_by_email.side_effect = RuntimeError("DB connection timeout")

        with pytest.raises(RuntimeError, match="DB connection timeout"):
            await user_svc.get_by_email("test@example.com")
