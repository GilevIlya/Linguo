from abc import abstractmethod
from uuid import UUID

from api.v1.models.files import Files
from api.v1.repositories.interfaces.IBaseRepository import IBaseRepository


class IFileRepository(IBaseRepository[Files, UUID]):
    @abstractmethod
    async def get_file_by_key(self, file_key: str) -> Files | None:
        """
        Retrieves a file by its unique storage key.

        Args:
            file_key (str): The unique key identifying the file in storage.

        Returns:
            Files | None: The file object if found, otherwise None.
        """
        pass

    @abstractmethod
    async def delete_file_by_key(self, file_key: str, owner_id: UUID) -> bool:
        pass