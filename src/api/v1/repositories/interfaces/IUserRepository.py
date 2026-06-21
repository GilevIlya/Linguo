from abc import abstractmethod
from uuid import UUID

from api.v1.models.users import User
from api.v1.repositories.interfaces.IBaseRepository import IBaseRepository


class IUserRepository(IBaseRepository[User, UUID]):
    """
    Repository interface for User entity.

    Extends the base CRUD interface with user-specific query methods.
    """

    @abstractmethod
    async def find_by_email(self, email: str) -> User | None:
        """Find a user by their email address. Returns None if not found."""
        pass


    @abstractmethod
    async def exists_by_email(self, email: str) -> bool:
        """Check whether a user with the given email already exists."""
        pass
