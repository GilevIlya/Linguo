from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Any

from api.v1.models.mixins.id_mixins import UUIDMixin

ModelType = TypeVar("ModelType", bound=UUIDMixin)
IDType = TypeVar("IDType")


class IBaseRepository(ABC, Generic[ModelType, IDType]):
    """
    The basic repository interface for CRUD operations.

    ModelType: The type of the data model
    IDType: Identifier type (int, str, UUID, etc.)
    """

    @abstractmethod
    async def create(self, entity: ModelType) -> ModelType:
        """Create a new entity"""
        pass

    @abstractmethod
    async def get_by_id(self, id: IDType, filters: dict[str, Any] | None = None) -> ModelType | None:
        """Get Entity by ID"""
        pass

    @abstractmethod
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 50,
        filters: dict[str, Any] | None = None
    ) -> list[ModelType]:
        """Get a list of all entities with pagination and filtering"""
        pass

    @abstractmethod
    async def update(self, obj: ModelType, data: dict[str, Any]) -> ModelType | None:
        """Update an existing entity"""
        pass

    @abstractmethod
    async def delete(self, id: IDType) -> bool:
        """Delete entity by ID. Returns True if deleted successfully"""
        pass

    @abstractmethod
    async def exists(self, id: IDType) -> bool:
        """Check the existence of an entity by ID"""
        pass

    @abstractmethod
    async def count(self, filters: dict[str, Any] | None = None) -> int:
        """Count the number of entities with optional filters"""
        pass
