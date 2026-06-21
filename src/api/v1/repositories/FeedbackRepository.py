from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.models import Feedback
from api.v1.repositories.interfaces.IFeedbackRepository import IFeedbackRepository
from api.v1.repositories.sqlalchemy_repository import SQLAlchemyBaseRepository


class FeedbackRepository(SQLAlchemyBaseRepository[Feedback, UUID], IFeedbackRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Feedback)
