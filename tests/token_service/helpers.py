import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

from api.v1.models import Token
from api.v1.services.tokens_service import TokenService


def _make_token_entity(
    user_id: uuid.UUID | None = None,
    token_hash: str = "somehash",
    expired_at: datetime | None = None,
) -> MagicMock:
    """Create a lightweight Token-like mock."""
    entity = MagicMock(spec=Token)
    entity.user_id = user_id or uuid.uuid4()
    entity.token = token_hash
    entity.expired_at = expired_at or (datetime.now(timezone.utc) + timedelta(days=7))
    return entity


def _hash(raw: str) -> str:
    """Mirror TokenService.__hash_token for assertions."""
    return TokenService._TokenService__hash_token(raw)  # type: ignore[attr-defined]

