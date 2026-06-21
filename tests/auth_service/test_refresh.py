import uuid
from unittest.mock import patch, AsyncMock

import pytest

from api.v1.services.auth_service import AuthService, TokensPair
from api.v1.services.exceptions.base_exceptions import AuthException
from api.v1.services.exceptions.error_codes.auth_error_codes import AuthErrorCodes
from tests.auth_service.helpers import _make_refresh_token, _make_token_entity


class TestRefresh:
    """Tests for AuthService.refresh()."""

    async def test_refresh_success(
        self, auth_service: AuthService, token_service: AsyncMock
    ):
        """Successful refresh rotates the token and returns a new TokensPair."""
        old_entity = _make_token_entity(user_id="user-123")
        token_service.rotate.return_value = old_entity
        new_refresh = _make_refresh_token(token="new_raw_token")
        token_service.create_token.return_value = new_refresh

        with patch("api.v1.services.auth_service.sign_jwt", return_value="new.access.jwt"):
            result = await auth_service.refresh("old_raw_token")

        assert isinstance(result, TokensPair)
        assert result.access_token == "new.access.jwt"
        assert result.refresh_token is new_refresh
        token_service.rotate.assert_awaited_once_with("old_raw_token")
        token_service.create_token.assert_awaited_once_with("user-123")

    async def test_refresh_invalid_token_raises_auth_exception(
        self, auth_service: AuthService, token_service: AsyncMock
    ):
        """If rotate() returns None, AuthException must be raised."""
        token_service.rotate.return_value = None

        with pytest.raises(AuthException) as exc_info:
            await auth_service.refresh("bogus_token")

        assert exc_info.value.error_code == AuthErrorCodes.INVALID_OR_EXPIRED_REFRESH_TOKEN.value
        assert "invalid" in exc_info.value.message.lower() or "expired" in exc_info.value.message.lower()

    async def test_refresh_expired_token_raises_auth_exception(
        self, auth_service: AuthService, token_service: AsyncMock
    ):
        """Expired token is handled by rotate() returning None."""
        token_service.rotate.return_value = None

        with pytest.raises(AuthException) as exc_info:
            await auth_service.refresh("expired_token")

        assert exc_info.value.error_code == AuthErrorCodes.INVALID_OR_EXPIRED_REFRESH_TOKEN.value

    async def test_refresh_does_not_create_token_on_failure(
        self, auth_service: AuthService, token_service: AsyncMock
    ):
        """If rotation fails, no new token should be created."""
        token_service.rotate.return_value = None

        with pytest.raises(AuthException):
            await auth_service.refresh("bad")

        token_service.create_token.assert_not_awaited()

    async def test_refresh_empty_token_raises(
        self, auth_service: AuthService, token_service: AsyncMock
    ):
        """Empty refresh token: rotate() returns None → AuthException."""
        token_service.rotate.return_value = None

        with pytest.raises(AuthException):
            await auth_service.refresh("")

    async def test_refresh_preserves_user_id(
        self, auth_service: AuthService, token_service: AsyncMock
    ):
        """The new token pair must be associated with the same user_id as the old one."""
        uid = str(uuid.uuid4())
        entity = _make_token_entity(user_id=uid)
        token_service.rotate.return_value = entity
        token_service.create_token.return_value = _make_refresh_token()

        with patch("api.v1.services.auth_service.sign_jwt", return_value="jwt"):
            await auth_service.refresh("tok")

        token_service.create_token.assert_awaited_once_with(uid)
