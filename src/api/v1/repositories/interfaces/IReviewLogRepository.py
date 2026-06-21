from abc import ABC
from uuid import UUID

from api.v1.models import ReviewLog
from api.v1.repositories.interfaces.IBaseRepository import IBaseRepository


class IReviewLogRepository(IBaseRepository[ReviewLog, UUID], ABC):
    ...
