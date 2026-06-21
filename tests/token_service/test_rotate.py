from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock

from api.v1.services.tokens_service import TokenService
from tests.token_service.helpers import _make_token_entity, _hash


class TestRotate:
    """Tests for TokenService.rotate(token)."""

    async def test_rotate_valid_token_returns_entity(
        self, token_svc: TokenService, token_repository: AsyncMock
    ):
        """A valid, non-expired token: rotate returns the Token entity."""
        entity = _make_token_entity()
        token_repository.get_by_token.return_value = entity
        token_repository.delete_by_token.return_value = True

        result = await token_svc.rotate("raw_tok")

        assert result is entity

    async def test_rotate_valid_token_deletes_it(
        self, token_svc: TokenService, token_repository: AsyncMock
    ):
        """After successful rotation the token must be deleted from the DB."""
        entity = _make_token_entity()
        token_repository.get_by_token.return_value = entity
        token_repository.delete_by_token.return_value = True

        await token_svc.rotate("raw_tok")

        token_repository.delete_by_token.assert_awaited_once_with(_hash("raw_tok"))

    async def test_rotate_token_not_found_returns_none(
        self, token_svc: TokenService, token_repository: AsyncMock
    ):
        """Token not in DB → returns None."""
        token_repository.get_by_token.return_value = None

        result = await token_svc.rotate("missing")

        assert result is None

    async def test_rotate_expired_token_returns_none(
        self, token_svc: TokenService, token_repository: AsyncMock
    ):
        """Expired token → returns None."""
        expired = _make_token_entity(
            expired_at=datetime.now(timezone.utc) - timedelta(hours=1),
        )
        token_repository.get_by_token.return_value = expired

        result = await token_svc.rotate("expired_tok")

        assert result is None

    async def test_rotate_expired_token_is_deleted(
        self, token_svc: TokenService, token_repository: AsyncMock
    ):
        """Expired token must still be cleaned up (deleted) from the DB."""
        expired = _make_token_entity(
            expired_at=datetime.now(timezone.utc) - timedelta(hours=1),
        )
        token_repository.get_by_token.return_value = expired

        await token_svc.rotate("expired_tok")

        token_repository.delete_by_token.assert_awaited_once_with(_hash("expired_tok"))

    async def test_rotate_hashes_token_before_lookup(
        self, token_svc: TokenService, token_repository: AsyncMock
    ):
        """get_by_token must receive the SHA-256 hash, not the raw string."""
        token_repository.get_by_token.return_value = None

        await token_svc.rotate("raw_value")

        token_repository.get_by_token.assert_awaited_once_with(_hash("raw_value"))

    async def test_rotate_not_found_does_not_call_delete(
        self, token_svc: TokenService, token_repository: AsyncMock
    ):
        """If token is not found, delete_by_token must NOT be called."""
        token_repository.get_by_token.return_value = None

        await token_svc.rotate("nope")

        token_repository.delete_by_token.assert_not_awaited()
