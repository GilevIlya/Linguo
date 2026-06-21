from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.models.users import User
from api.v1.repositories.interfaces.IUserRepository import IUserRepository
from .sqlalchemy_repository import SQLAlchemyBaseRepository


class UserRepository(SQLAlchemyBaseRepository[User, UUID], IUserRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, User)
    
    async def find_by_email(self, email: str) -> User | None:
        stmt = select(self.model).where(self.model.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def exists_by_email(self, email: str) -> bool:
        stmt = select(1).where(self.model.email == email).limit(1)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None
