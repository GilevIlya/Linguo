from api.v1.repositories.sqlalchemy_repository import SQLAlchemyBaseRepository
from api.v1.repositories.interfaces.IProfileRepository import IProfileRepository

from api.v1.models.profiles import Profile
from uuid import UUID
from sqlalchemy import select
from typing import Any

class ProfileRepository(SQLAlchemyBaseRepository[Profile, UUID], IProfileRepository):
    def __init__(self, session):
        super().__init__(session, Profile)

    async def get_by_user_id(self, user_id: UUID) -> Profile | None:
        stmt = select(self.model).where(self.model.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def update(self, obj: Profile, data: dict[str, Any]) -> Profile:
        for key, value in data.items():
            setattr(obj, key, value)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj