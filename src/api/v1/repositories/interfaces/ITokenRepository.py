from abc import abstractmethod
from uuid import UUID

from api.v1.models import Token
from api.v1.repositories.interfaces.IBaseRepository import IBaseRepository


class ITokenRepository(IBaseRepository[Token, UUID]):

    @abstractmethod
    async def get_by_token(self, token: str) -> Token | None:
        """
        Finds a token by its value.

        Args:
            token (str): The token string to search for.

        Returns:
            Token | None: The found token object or None if not found.
        """
        pass

    @abstractmethod
    async def delete_by_token(self, token: str) -> bool:
        """
        Deletes the given token from the repository.

        Args:
            token (str): The token string to delete.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        pass

    @abstractmethod
    async def deactivate_all_for_user(self, user_id: UUID) -> int:
        """Soft-delete all active refresh tokens for a user and return affected count."""
        pass

