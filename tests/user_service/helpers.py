import uuid
from unittest.mock import MagicMock

from api.v1.models import User


def _make_user(
    user_id: uuid.UUID | None = None,
    username: str = "testuser",
    email: str = "test@example.com",
    password: str = "hashed_password_123",
) -> MagicMock:
    """Создаёт легковесный mock-объект User для тестов."""
    user = MagicMock(spec=User)
    user.id = user_id or uuid.uuid4()
    user.username = username
    user.email = email
    user.password = password
    return user

