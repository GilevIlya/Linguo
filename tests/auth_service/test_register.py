from unittest.mock import AsyncMock, patch

import pytest

from api.v1.models import User
from api.v1.services.auth_service import AuthService, TokensPair
from api.v1.services.exceptions.base_exceptions import AlreadyExistsException
from api.v1.services.exceptions.error_codes.user_error_codes import UserErrorCodes
from tests.auth_service.helpers import _make_refresh_token


class TestRegister:
    """Tests for AuthService.register()."""

    async def test_register_success(
        self, auth_service: AuthService, user_service: AsyncMock, token_service: AsyncMock
    ):
        """Successful registration returns a TokensPair and delegates hashing."""
        refresh = _make_refresh_token()
        token_service.create_token.return_value = refresh

        with patch(
            "api.v1.services.auth_service.hash_password", return_value="hashed_pw"
        ) as mock_hash, patch(
            "api.v1.services.auth_service.sign_jwt", return_value="access.jwt.token"
        ):
            result = await auth_service.register("alice", "alice@example.com", "Pa$$w0rd")

        # Assertions
        assert isinstance(result, TokensPair)
        assert result.access_token == "access.jwt.token"
        assert result.refresh_token is refresh

        # hash_password must be called with the raw password
        mock_hash.assert_called_once_with("Pa$$w0rd")

        # user_service.create_user must receive a User-like object
        user_service.create_user.assert_awaited_once()
        created_user = user_service.create_user.call_args[0][0]
        assert isinstance(created_user, User)
        assert created_user.email == "alice@example.com"
        assert created_user.password == "hashed_pw"

        # token_service.create_token must receive the user's id
        token_service.create_token.assert_awaited_once()

    async def test_register_duplicate_email_raises(
        self, auth_service: AuthService, user_service: AsyncMock
    ):
        """If user_service.create_user raises AlreadyExistsException it propagates."""
        user_service.create_user.side_effect = AlreadyExistsException(
            error_code=UserErrorCodes.EMAIL_ALREADY_IN_USE.value,
            message="User with this email already exists",
        )

        with patch("api.v1.services.auth_service.hash_password", return_value="h"):
            with pytest.raises(AlreadyExistsException) as exc_info:
                await auth_service.register("bob", "dup@example.com", "pass")

        assert exc_info.value.error_code == UserErrorCodes.EMAIL_ALREADY_IN_USE.value

    async def test_register_calls_hash_in_thread(
        self, auth_service: AuthService, token_service: AsyncMock
    ):
        """hash_password is offloaded to asyncio.to_thread so it doesn't block the loop."""
        token_service.create_token.return_value = _make_refresh_token()

        with patch(
            "api.v1.services.auth_service.asyncio.to_thread",
            new_callable=AsyncMock,
            return_value="threaded_hash",
        ) as mock_to_thread, patch(
            "api.v1.services.auth_service.sign_jwt", return_value="jwt"
        ):
            await auth_service.register("carol", "carol@example.com", "secret")

        # to_thread should be called with hash_password and the raw password
        mock_to_thread.assert_awaited_once()
        args = mock_to_thread.call_args[0]
        # First arg is the function, second is the password
        assert args[1] == "secret"

    async def test_register_empty_username(
        self, auth_service: AuthService, token_service: AsyncMock
    ):
        """Register with an empty username still delegates to user_service (validation is in the layer above)."""
        token_service.create_token.return_value = _make_refresh_token()

        with patch("api.v1.services.auth_service.hash_password", return_value="h"), patch(
            "api.v1.services.auth_service.sign_jwt", return_value="jwt"
        ):
            result = await auth_service.register("", "a@b.com", "pwd")

        assert isinstance(result, TokensPair)

    async def test_register_empty_password(
        self, auth_service: AuthService, token_service: AsyncMock
    ):
        """Register with an empty password: hash_password is still called (no guard in service)."""
        token_service.create_token.return_value = _make_refresh_token()

        with patch(
            "api.v1.services.auth_service.hash_password", return_value="hashed_empty"
        ) as mock_hash, patch("api.v1.services.auth_service.sign_jwt", return_value="jwt"):
            await auth_service.register("user", "u@e.com", "")

        mock_hash.assert_called_once_with("")

    async def test_register_empty_email(
        self, auth_service: AuthService, token_service: AsyncMock
    ):
        """Register with an empty email delegates to user_service without raising."""
        token_service.create_token.return_value = _make_refresh_token()

        with patch("api.v1.services.auth_service.hash_password", return_value="h"), patch(
            "api.v1.services.auth_service.sign_jwt", return_value="jwt"
        ):
            result = await auth_service.register("user", "", "pwd")

        assert isinstance(result, TokensPair)

