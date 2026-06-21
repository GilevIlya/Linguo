import hashlib
import logging
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from uuid import UUID

from api.v1.configs.security_config import security_config
from api.v1.models import Token
from api.v1.repositories.interfaces.ITokenRepository import ITokenRepository

logger = logging.getLogger("app")

@dataclass(frozen=True)
class RefreshToken:
    token: str
    exp: datetime

class TokenService:
    TOKEN_LENGTH = 192

    def __init__(self, token_repository: ITokenRepository):
        self.token_repository = token_repository

    async def create_token(self, user_id: UUID) -> RefreshToken:
        """
        Creates a new refresh token for a user.

        Args:
            user_id (UUID): The unique identifier of the user.

        Returns:
            RefreshToken: The generated refresh token object containing the token string and expiration date.
        """
        token = self.__generate_token()
        token_entity = Token(
            user_id=user_id,
            expired_at=self.__get_expired_at(),
            token=self.__hash_token(token),
        )
        await self.token_repository.create(token_entity)

        return RefreshToken(token=token, exp=token_entity.expired_at)

    async def deactivate_token(self, token: str) -> bool:
        """
        Deactivates a refresh token.

        Args:
            token (str): The token string to deactivate.

        Returns:
            bool: True if the token was successfully deactivated, False otherwise.
        """
        result = await self.token_repository.delete_by_token(self.__hash_token(token))
        return result

    async def deactivate_all_for_user(self, user_id: UUID) -> int:
        """Invalidate all active refresh tokens for a user."""
        return await self.token_repository.deactivate_all_for_user(user_id)

    async def rotate(self, token: str) -> Token | None:
        """
        Validates the given raw refresh token and, if valid, deletes it to prepare for rotation.

        Fetches the token record from the database in a single query. If the token
        does not exist or has expired, it is cleaned up and None is returned.
        If the token is valid, it is deleted (consumed) and the record is returned
        so the caller can issue a new token for the same user.

        Args:
            token (str): The raw (unhashed) refresh token string.

        Returns:
            Token | None: The consumed token record if valid, or None if invalid/expired.
        """
        hashed = self.__hash_token(token)
        token_entity = await self.token_repository.get_by_token(hashed)
        if not token_entity:
            return None
        if token_entity.expired_at < datetime.now(timezone.utc):
            await self.token_repository.delete_by_token(hashed)
            return None
        if not await self.token_repository.delete_by_token(hashed):
            return None
        return token_entity

    @staticmethod
    def __hash_token(token: str) -> str:
        """
        Hashes the token using SHA-256.

        Args:
            token (str): The raw token string.

        Returns:
            str: The hashed token string.
        """
        return hashlib.sha256(token.encode()).hexdigest()

    def __generate_token(self) -> str:
        """
        Generates a random secure token string.

        Returns:
            str: A random string of alphanumeric characters.
        """
        return secrets.token_urlsafe(self.TOKEN_LENGTH)

    def __get_expired_at(self) -> datetime:
        """
        Calculates the expiration datetime for a new token.

        Returns:
            datetime: The expiration datetime.
        """
        return datetime.now(timezone.utc) + timedelta(seconds=security_config.REFRESH_TOKEN_EXPIRE_SEC)
