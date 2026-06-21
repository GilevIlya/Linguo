from uuid import UUID
from abc import abstractmethod

from api.v1.models.profiles import Profile
from api.v1.repositories.interfaces.IBaseRepository import IBaseRepository


class IProfileRepository(IBaseRepository[Profile, UUID]):
    
    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> Profile | None:
        """
        Retrieves a Profile by the user's ID.

        Args:
            user_id (UUID): The unique identifier of the user.

        Returns:
            Optional[Profile]: The Profile object if found, otherwise None.
        """
        pass