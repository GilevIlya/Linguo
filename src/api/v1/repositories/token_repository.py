from datetime import datetime, timezone
from typing import override
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.models.tokens import Token
from api.v1.repositories.interfaces.ITokenRepository import ITokenRepository
from .sqlalchemy_repository import SQLAlchemyBaseRepository


class TokenRepository(SQLAlchemyBaseRepository[Token, UUID], ITokenRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Token)
        
    @override
    async def get_by_token(self, token: str) -> Token | None:
        stmt = select(self.model).where(
            self.model.token == token,
            self.model.deleted_at.is_(None),  # """Это надо чтобы soft_deleted токены не возвращались при запросе"""
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    @override
    async def delete_by_token(self, token: str) -> bool:
        stmt = (
            update(self.model)
            .where(
                self.model.token == token,
                self.model.deleted_at.is_(None)
            )
            .values(deleted_at=datetime.now(timezone.utc))
            .returning(self.model.id)
        )

        result = await self.session.execute(stmt)
        await self.session.commit()

        return result.first() is not None

    @override
    async def deactivate_all_for_user(self, user_id: UUID) -> int:
        stmt = (
            update(self.model)
            .where(
                self.model.user_id == user_id,
                self.model.deleted_at.is_(None),
            )
            .values(deleted_at=datetime.now(timezone.utc))
            .returning(self.model.id)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return len(result.fetchall())
