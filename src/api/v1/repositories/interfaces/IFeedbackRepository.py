from abc import ABC
from uuid import UUID

from api.v1.models import Feedback
from api.v1.repositories.interfaces.IBaseRepository import IBaseRepository


class IFeedbackRepository(IBaseRepository[Feedback, UUID], ABC):
    ...
