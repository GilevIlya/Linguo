import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

from api.v1.models import User, Token
from api.v1.services.tokens_service import RefreshToken


def _make_user(
    user_id: str | None = None,
    username: str = "testuser",
    email: str = "test@example.com",
    password: str = "hashed_pw",
) -> MagicMock:
    """Create a lightweight User-like mock."""
    user = MagicMock(spec=User)
    user.id = user_id or str(uuid.uuid4())
    user.username = username
    user.email = email
    user.password = password
    return user


def _make_refresh_token(
    token: str = "raw_refresh_token",
    exp: datetime | None = None,
) -> RefreshToken:
    return RefreshToken(token=token, exp=exp or datetime.now() + timedelta(days=7))


def _make_token_entity(
    user_id: str | None = None,
    expired_at: datetime | None = None,
) -> MagicMock:
    """Mimic a Token ORM entity returned by rotate()."""
    entity = MagicMock(spec=Token)
    entity.user_id = user_id or str(uuid.uuid4())
    entity.expired_at = expired_at or (datetime.now(timezone.utc) + timedelta(days=7))
    return entity