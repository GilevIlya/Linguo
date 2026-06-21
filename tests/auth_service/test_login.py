from unittest.mock import AsyncMock, patch

import pytest

from api.v1.services.auth_service import AuthService, TokensPair
from api.v1.services.exceptions.base_exceptions import AuthException, NotFoundException
from api.v1.services.exceptions.error_codes.auth_error_codes import AuthErrorCodes
from api.v1.services.exceptions.error_codes.user_error_codes import UserErrorCodes
from tests.auth_service.helpers import _make_user, _make_refresh_token


class TestLogin:
    """Tests for AuthService.login()."""

    async def test_login_success(
        self, auth_service: AuthService, user_service: AsyncMock, token_service: AsyncMock
    ):
        user = _make_user(password="hashed_pw")
        user_service.get_by_email.return_value = user
        refresh = _make_refresh_token()
        token_service.create_token.return_value = refresh

        with patch(
            "api.v1.services.auth_service.check_password", return_value=True
        ), patch("api.v1.services.auth_service.sign_jwt", return_value="access.jwt"):
            result = await auth_service.login("test@example.com", "correct_pw")

        assert isinstance(result, TokensPair)
        assert result.access_token == "access.jwt"
        assert result.refresh_token is refresh
        user_service.get_by_email.assert_awaited_once_with("test@example.com")
        token_service.create_token.assert_awaited_once_with(user.id)

    async def test_login_user_not_found_raises_auth_exception(
        self, auth_service: AuthService, user_service: AsyncMock
    ):
        """When user_service.get_by_email raises NotFoundException, AuthException is raised."""
        user_service.get_by_email.side_effect = NotFoundException(
            error_code=UserErrorCodes.USER_NOT_FOUND.value,
            message="User with this email not found",
        )

        with pytest.raises(AuthException) as exc_info:
            await auth_service.login("ghost@example.com", "any")

        assert exc_info.value.error_code == AuthErrorCodes.EMAIL_OR_PASSWORD_INCORRECT.value
        assert "incorrect" in exc_info.value.message.lower()

    async def test_login_wrong_password_raises_auth_exception(
        self, auth_service: AuthService, user_service: AsyncMock
    ):
        user = _make_user()
        user_service.get_by_email.return_value = user

        with patch("api.v1.services.auth_service.check_password", return_value=False):
            with pytest.raises(AuthException) as exc_info:
                await auth_service.login("test@example.com", "wrong")

        assert exc_info.value.error_code == AuthErrorCodes.EMAIL_OR_PASSWORD_INCORRECT.value

    async def test_login_check_password_runs_in_thread(
        self, auth_service: AuthService, user_service: AsyncMock, token_service: AsyncMock
    ):
        """check_password is offloaded to asyncio.to_thread."""
        user = _make_user(password="hash")
        user_service.get_by_email.return_value = user
        token_service.create_token.return_value = _make_refresh_token()

        with patch(
            "api.v1.services.auth_service.asyncio.to_thread",
            new_callable=AsyncMock,
            return_value=True,
        ) as mock_to_thread, patch(
            "api.v1.services.auth_service.sign_jwt", return_value="jwt"
        ):
            await auth_service.login("e@e.com", "pw")

        mock_to_thread.assert_awaited_once()
        args = mock_to_thread.call_args[0]
        # check_password(password, hashed)
        assert args[1] == "pw"
        assert args[2] == "hash"

    async def test_login_empty_email_triggers_not_found(
        self, auth_service: AuthService, user_service: AsyncMock
    ):
        """Empty email: user_service raises NotFoundException → AuthException."""
        user_service.get_by_email.side_effect = NotFoundException(
            error_code=UserErrorCodes.USER_NOT_FOUND.value,
            message="Not found",
        )

        with pytest.raises(AuthException):
            await auth_service.login("", "password")

    async def test_login_empty_password_wrong(
        self, auth_service: AuthService, user_service: AsyncMock
    ):
        """Empty password: user exists but password does not match."""
        user = _make_user()
        user_service.get_by_email.return_value = user

        with patch("api.v1.services.auth_service.check_password", return_value=False):
            with pytest.raises(AuthException):
                await auth_service.login("test@example.com", "")

    async def test_login_does_not_create_token_on_wrong_password(
        self, auth_service: AuthService, user_service: AsyncMock, token_service: AsyncMock
    ):
        """Token must NOT be created if the password is wrong."""
        user = _make_user()
        user_service.get_by_email.return_value = user

        with patch("api.v1.services.auth_service.check_password", return_value=False):
            with pytest.raises(AuthException):
                await auth_service.login("x@x.com", "bad")

        token_service.create_token.assert_not_awaited()

    async def test_login_does_not_create_token_on_user_not_found(
        self, auth_service: AuthService, user_service: AsyncMock, token_service: AsyncMock
    ):
        """Token must NOT be created if the user is not found."""
        user_service.get_by_email.side_effect = NotFoundException(
            error_code=UserErrorCodes.USER_NOT_FOUND.value, message="nope"
        )

        with pytest.raises(AuthException):
            await auth_service.login("x@x.com", "any")

        token_service.create_token.assert_not_awaited()

    async def test_login_error_message_is_generic(
        self, auth_service: AuthService, user_service: AsyncMock
    ):
        """Auth errors must NOT reveal whether the email or password was wrong (security)."""
        # Case 1: user not found
        user_service.get_by_email.side_effect = NotFoundException(
            error_code=UserErrorCodes.USER_NOT_FOUND.value, message="nf"
        )
        with pytest.raises(AuthException) as exc1:
            await auth_service.login("a@a.com", "pw")

        # Case 2: wrong password
        user_service.get_by_email.side_effect = None
        user_service.get_by_email.return_value = _make_user()
        with patch("api.v1.services.auth_service.check_password", return_value=False):
            with pytest.raises(AuthException) as exc2:
                await auth_service.login("a@a.com", "pw")

        # Both messages and error_codes must be identical
        assert exc1.value.error_code == exc2.value.error_code
        assert exc1.value.message == exc2.value.message