from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.models import ReviewLog
from api.v1.repositories.interfaces.IReviewLogRepository import IReviewLogRepository
from api.v1.repositories.sqlalchemy_repository import SQLAlchemyBaseRepository


class ReviewLogRepository(IReviewLogRepository, SQLAlchemyBaseRepository[ReviewLog, UUID]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, ReviewLog)
