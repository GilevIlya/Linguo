from uuid import UUID

from fastapi import APIRouter, Depends

from api.v1.models.feedbacks import FeedbackType
from api.v1.routers.security import get_current_user_id
from api.v1.routers.utils.dependencies import get_feedback_service
from api.v1.schemas.requests.feedback import CreateFeedbackRequest
from api.v1.schemas.responses.base_response import BaseMessageResponse
from api.v1.services.FeedbackService import FeedbackService

feedback_router = APIRouter(
    prefix="/feedbacks",
    tags=["feedbacks"],


)

@feedback_router.post(
    "",
    status_code=201,
    response_model=BaseMessageResponse[str],
    responses={
        401: {"description": "Unauthorized"},
    }
)
async def create_feedback(
        request: CreateFeedbackRequest,
        user_id: UUID = Depends(get_current_user_id),
        feedback_service: FeedbackService = Depends(get_feedback_service),
) -> BaseMessageResponse[str]:
    """Create new user feedback.

    Args:
        request: Validated feedback data including message, type, and fill time.
        user_id: The ID of the user creating the feedback.
        feedback_service: The service responsible for creating feedback.

    Returns:
        Success confirmation message.

    Raises:
        401: If the user is not authenticated.
    """
    await feedback_service.create_feedback(
        user_id=user_id,
        message=request.message,
        type=FeedbackType(request.feedback_type.value),
        form_filled_time_ms=request.form_filled_time_ms,
    )
    return BaseMessageResponse(
        message="Feedback created",
        data=None,
    )
