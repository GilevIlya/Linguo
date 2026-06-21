from typing import Generic, Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.repositories.interfaces.IBaseRepository import IBaseRepository, IDType, ModelType


class SQLAlchemyBaseRepository(IBaseRepository[ModelType, IDType], Generic[ModelType, IDType]):
    def __init__(self, session: AsyncSession, model: type[ModelType]):
        self.session = session
        self.model = model

    async def create(self, entity: ModelType) -> ModelType:
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def get_by_id(self, id: IDType, filters: dict[str, Any] | None = None) -> ModelType | None:
        stmt = select(self.model).where(self.model.id == id)

        if filters:
            for field, value in filters.items():
                column = getattr(self.model, field)
                stmt = stmt.where(column == value)
                
        result = await self.session.execute(stmt)   
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 50,
        filters: dict[str, Any] | None = None
    ) -> list[ModelType]:

        stmt = select(self.model)

        if filters:
            for field, value in filters.items():
                column = getattr(self.model, field)
                stmt = stmt.where(column == value)

        stmt = stmt.offset(skip).limit(limit)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update(self, obj: ModelType, data: dict[str, Any]) -> ModelType | None:
        for key, value in data.items():
            setattr(obj, key, value)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def delete(self, id: IDType) -> bool:
        del_obj = await self.session.get(self.model, id)
        if not del_obj:
            return False

        await self.session.delete(del_obj)
        await self.session.commit()
        return True

    async def exists(self, id: IDType) -> bool:
        result = await self.session.execute(
            select(1).where(self.model.id == id).limit(1)
        )
        return result.scalar_one_or_none() is not None


    async def count(self, filters: dict[str, Any] | None = None) -> int:
        query = select(func.count()).select_from(self.model)

        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    query = query.where(getattr(self.model, key) == value)

        result = await self.session.execute(query)
        return result.scalar_one()