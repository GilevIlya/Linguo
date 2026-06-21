import uuid
from unittest.mock import AsyncMock

import pytest

from api.v1.models.feedbacks import FeedbackType, FeedbackStatus
from api.v1.services.FeedbackService import FeedbackService
from api.v1.services.exceptions.base_exceptions import BusinessLogicException
from api.v1.services.exceptions.error_codes.base import BaseErrorCodes
from api.v1.services.exceptions.error_codes.feedback_error_codes import FeedbackErrorCodes


class TestCreateFeedback:
    async def test_create_feedback_success(self, feedback_svc: FeedbackService, feedback_repository: AsyncMock):
        user_id = uuid.uuid4()
        message = "Important feedback"
        type = FeedbackType.BUG
        time_ms = 5000
        result = await feedback_svc.create_feedback(
            user_id=user_id,
            message=message,
            type=type,
            form_filled_time_ms=time_ms,
        )
        assert result.user_id == user_id
        assert result.message == message
        assert result.type == type
        assert result.form_fill_time_ms == time_ms
        assert result.status == FeedbackStatus.CREATED
        feedback_repository.create.assert_awaited_once_with(result)

    async def test_create_feedback_empty_message(self, feedback_svc: FeedbackService, feedback_repository: AsyncMock):
        with pytest.raises(BusinessLogicException) as exc_info:
            await feedback_svc.create_feedback(
                user_id=uuid.uuid4(),
                message="   ",
                type=FeedbackType.WISH,
                form_filled_time_ms=5000,
            )
        assert exc_info.value.error_code == FeedbackErrorCodes.FEEDBACK_MESSAGE_IS_INVALID.value
        feedback_repository.create.assert_not_called()

    async def test_create_feedback_invalid_time(self, feedback_svc: FeedbackService, feedback_repository: AsyncMock):
        with pytest.raises(BusinessLogicException) as exc_info:
            await feedback_svc.create_feedback(
                user_id=uuid.uuid4(),
                message="Valid message",
                type=FeedbackType.OTHER,
                form_filled_time_ms=0,
            )
        assert exc_info.value.error_code == BaseErrorCodes.INVALID_FORM_FILLED_TIME.value
        feedback_repository.create.assert_not_called()
