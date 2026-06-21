from unittest.mock import AsyncMock

import pytest

from api.v1.repositories.interfaces.IFeedbackRepository import IFeedbackRepository
from api.v1.services.FeedbackService import FeedbackService
from api.v1.services.user_service import UserService


@pytest.fixture
def feedback_repository() -> AsyncMock:
    return AsyncMock(spec=IFeedbackRepository)

@pytest.fixture
def feedback_svc(feedback_repository: AsyncMock, user_svc: UserService) -> FeedbackService:
    return FeedbackService(feedback_repository=feedback_repository, user_service=user_svc)
