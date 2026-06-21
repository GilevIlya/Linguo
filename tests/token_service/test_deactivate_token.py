from unittest.mock import AsyncMock

from api.v1.services.tokens_service import TokenService
from tests.token_service.helpers import _hash


class TestDeactivateToken:
    """Tests for TokenService.deactivate_token(token)."""

    async def test_deactivate_token_success(
        self, token_svc: TokenService, token_repository: AsyncMock
    ):
        """When the token exists and is deleted, returns True."""
        token_repository.delete_by_token.return_value = True

        result = await token_svc.deactivate_token("raw_token")

        assert result is True

    async def test_deactivate_token_not_found(
        self, token_svc: TokenService, token_repository: AsyncMock
    ):
        """When the token does not exist, returns False."""
        token_repository.delete_by_token.return_value = False

        result = await token_svc.deactivate_token("missing_token")

        assert result is False

    async def test_deactivate_token_hashes_before_delete(
        self, token_svc: TokenService, token_repository: AsyncMock
    ):
        """The repository receives the SHA-256 hash, not the raw token."""
        token_repository.delete_by_token.return_value = True
        raw = "my_secret_token"

        await token_svc.deactivate_token(raw)

        token_repository.delete_by_token.assert_awaited_once_with(_hash(raw))
