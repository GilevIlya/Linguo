from unittest.mock import AsyncMock

from api.v1.services.auth_service import AuthService


class TestLogout:
    """Tests for AuthService.logout()."""

    async def test_logout_success(
        self, auth_service: AuthService, token_service: AsyncMock
    ):
        """Successful logout deactivates the token and returns None."""
        token_service.deactivate_token.return_value = True

        result = await auth_service.logout("some_refresh_token")

        assert result is None
        token_service.deactivate_token.assert_awaited_once_with("some_refresh_token")

    async def test_logout_token_not_found(
        self, auth_service: AuthService, token_service: AsyncMock
    ):
        """If the token does not exist or is already expired, logout still succeeds (no exception)."""
        token_service.deactivate_token.return_value = False

        result = await auth_service.logout("nonexistent_token")

        assert result is None
        token_service.deactivate_token.assert_awaited_once_with("nonexistent_token")

    async def test_logout_empty_token(
        self, auth_service: AuthService, token_service: AsyncMock
    ):
        """Empty token string is forwarded to token_service without raising."""
        token_service.deactivate_token.return_value = False

        result = await auth_service.logout("")

        assert result is None
        token_service.deactivate_token.assert_awaited_once_with("")

    async def test_logout_called_multiple_times_is_idempotent(
        self, auth_service: AuthService, token_service: AsyncMock
    ):
        """Multiple logouts with the same token should not raise."""
        token_service.deactivate_token.side_effect = [True, False]

        await auth_service.logout("tok")
        await auth_service.logout("tok")

        assert token_service.deactivate_token.await_count == 2