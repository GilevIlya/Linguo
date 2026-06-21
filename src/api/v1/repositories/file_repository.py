from api.v1.models.files import Files
from api.v1.repositories.interfaces.IFileRepository import IFileRepository
from .sqlalchemy_repository import SQLAlchemyBaseRepository


from uuid import UUID
from sqlalchemy import select, delete
from typing import override

class FileRepository(SQLAlchemyBaseRepository[Files, UUID], IFileRepository):
    def __init__(self, session):
        super().__init__(session, Files)

    @override
    async def get_file_by_key(self, file_key: str) -> Files | None:
        stmt = select(self.model).where(self.model.file_key == file_key)

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    @override
    async def delete_file_by_key(self, file_key, owner_id) -> bool:
        stmt = delete(self.model).where(
            self.model.file_key == file_key,
            self.model.owner_id == owner_id
        )
        await self.session.execute(stmt)
        await self.session.commit()
        return True
