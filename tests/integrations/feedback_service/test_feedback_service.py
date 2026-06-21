import pytest

from api.v1.models import User
from api.v1.models.feedbacks import FeedbackType, FeedbackStatus
from api.v1.services.FeedbackService import FeedbackService
from api.v1.services.exceptions.base_exceptions import BusinessLogicException
from api.v1.services.exceptions.error_codes.base import BaseErrorCodes
from api.v1.services.exceptions.error_codes.feedback_error_codes import FeedbackErrorCodes


async def test_create_feedback_success(feedback_service: FeedbackService, new_user: User):
    message = "Integration test message"
    form_time = 1500
    feedback = await feedback_service.create_feedback(
        user_id=new_user.id,
        message=message,
        type=FeedbackType.WISH,
        form_filled_time_ms=form_time,
    )
    assert feedback.id is not None
    assert feedback.user_id == new_user.id
    assert feedback.message == message
    assert feedback.type == FeedbackType.WISH
    assert feedback.status == FeedbackStatus.CREATED
    assert feedback.form_fill_time_ms == form_time


async def test_create_feedback_empty_message(feedback_service: FeedbackService, new_user: User):
    with pytest.raises(BusinessLogicException) as exc_info:
        await feedback_service.create_feedback(
            user_id=new_user.id,
            message="",
            type=FeedbackType.BUG,
            form_filled_time_ms=1000,
        )
    assert exc_info.value.error_code == FeedbackErrorCodes.FEEDBACK_MESSAGE_IS_INVALID.value


async def test_create_feedback_invalid_time(feedback_service: FeedbackService, new_user: User):
    with pytest.raises(BusinessLogicException) as exc_info:
        await feedback_service.create_feedback(
            user_id=new_user.id,
            message="Some text",
            type=FeedbackType.OTHER,
            form_filled_time_ms=-1,
        )
    assert exc_info.value.error_code == BaseErrorCodes.INVALID_FORM_FILLED_TIME.value
