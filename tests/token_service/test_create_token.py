import uuid
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock

from api.v1.configs.security_config import security_config
from api.v1.services.tokens_service import TokenService, RefreshToken
from tests.token_service.helpers import _hash, _make_token_entity


class TestCreateToken:
    """Tests for TokenService.create_token(user_id)."""

    async def test_create_token_has_sufficient_length(self, token_svc, token_repository):
        result = await token_svc.create_token(uuid.uuid4())
        assert len(result.token) >= 200, "Token is too short for security requirements"

    async def test_create_token_expiration_matches_config(self, token_svc, token_repository):
        before = datetime.now(timezone.utc)
        result = await token_svc.create_token(uuid.uuid4())
        after = datetime.now(timezone.utc)

        expected_min = before + timedelta(seconds=security_config.REFRESH_TOKEN_EXPIRE_SEC)
        expected_max = after + timedelta(seconds=security_config.REFRESH_TOKEN_EXPIRE_SEC + 1)
        assert expected_min <= result.exp <= expected_max

    async def test_rotate_delete_fails_after_get(self, token_svc, token_repository):
        """If another process deletes the token between get and delete."""
        entity = _make_token_entity()
        token_repository.get_by_token.return_value = entity
        token_repository.delete_by_token.return_value = False  # already deleted
        result = await token_svc.rotate("raw_tok")
        assert result is None

    async def test_create_token_returns_refresh_token(
        self, token_svc: TokenService, token_repository: AsyncMock
    ):
        """create_token must return a RefreshToken dataclass with token and exp."""
        result = await token_svc.create_token(uuid.uuid4())

        assert isinstance(result, RefreshToken)
        assert isinstance(result.token, str)
        assert len(result.token) > 0
        assert isinstance(result.exp, datetime)

    async def test_create_token_calls_repository_create(
        self, token_svc: TokenService, token_repository: AsyncMock
    ):
        """repository.create() is called exactly once."""
        await token_svc.create_token(uuid.uuid4())

        token_repository.create.assert_awaited_once()

    async def test_create_token_passes_user_id_to_entity(
        self, token_svc: TokenService, token_repository: AsyncMock
    ):
        """The Token entity passed to repository.create() carries the given user_id."""
        id_ = uuid.uuid4()
        await token_svc.create_token(id_)

        entity = token_repository.create.call_args[0][0]
        assert entity.user_id == id_

    async def test_create_token_token_is_hashed_before_saving(
        self, token_svc: TokenService, token_repository: AsyncMock
    ):
        """The token stored in the entity must be a SHA-256 hex digest (64 chars)."""
        result = await token_svc.create_token(uuid.uuid4())

        entity = token_repository.create.call_args[0][0]
        assert len(entity.token) == 64  # SHA-256 hex length
        assert entity.token == _hash(result.token)

    async def test_create_token_raw_token_not_stored(
        self, token_svc: TokenService, token_repository: AsyncMock
    ):
        """The raw token returned to caller must NOT equal the hashed value in the entity."""
        result = await token_svc.create_token(uuid.uuid4())

        entity = token_repository.create.call_args[0][0]
        assert result.token != entity.token

    async def test_create_token_expiration_is_in_future(
        self, token_svc: TokenService, token_repository: AsyncMock
    ):
        """The expiration datetime must be strictly in the future."""
        result = await token_svc.create_token(uuid.uuid4())

        assert result.exp > datetime.now(timezone.utc)

