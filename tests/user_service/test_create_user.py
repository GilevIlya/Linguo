from unittest.mock import AsyncMock

import pytest
from sqlalchemy.exc import IntegrityError

from api.v1.services.exceptions.base_exceptions import AlreadyExistsException
from api.v1.services.exceptions.error_codes.user_error_codes import UserErrorCodes
from api.v1.services.user_service import UserService
from tests.user_service.helpers import _make_user


class TestCreateUser:
    async def test_create_user_returns_created_entity(
        self, user_svc: UserService, user_repository: AsyncMock
    ):
        user_in = _make_user()
        expected = _make_user(user_id=user_in.id, email=user_in.email)
        user_repository.create.return_value = expected

        result = await user_svc.create_user(user_in)

        assert result is expected

    async def test_create_user_calls_repository_create_once(
        self, user_svc: UserService, user_repository: AsyncMock
    ):
        user_in = _make_user()
        user_repository.create.return_value = user_in

        await user_svc.create_user(user_in)

        user_repository.create.assert_awaited_once_with(user_in)

    async def test_create_user_passes_exact_entity_to_repository(
        self, user_svc: UserService, user_repository: AsyncMock
    ):
        user_in = _make_user(email="specific@mail.com")
        user_repository.create.return_value = user_in

        await user_svc.create_user(user_in)

        actual_arg = user_repository.create.call_args[0][0]
        assert actual_arg is user_in

    async def test_create_user_duplicate_email_error(
        self, user_svc: UserService, user_repository: AsyncMock
    ):
        user_repository.create.side_effect = IntegrityError(
            statement="INSERT INTO users ...",
            params={},
            orig=Exception("duplicate key"),
        )

        with pytest.raises(AlreadyExistsException) as exc_info:
            await user_svc.create_user(_make_user())

        assert exc_info.value.error_code == UserErrorCodes.EMAIL_ALREADY_IN_USE.value

    async def test_create_user_repository_returns_none(
        self, user_svc: UserService, user_repository: AsyncMock
    ):
        user_repository.create.return_value = None

        result = await user_svc.create_user(_make_user())

        assert result is None

