from logging import getLogger
from uuid import UUID

from api.v1.models import Feedback
from api.v1.models.feedbacks import FeedbackStatus, FeedbackType
from api.v1.repositories.interfaces.IFeedbackRepository import IFeedbackRepository
from api.v1.services.exceptions.base_exceptions import BusinessLogicException
from api.v1.services.exceptions.error_codes.base import BaseErrorCodes
from api.v1.services.exceptions.error_codes.feedback_error_codes import FeedbackErrorCodes
from api.v1.services.user_service import UserService

logger = getLogger("app")


class FeedbackService:
    def __init__(
            self,
            feedback_repository: IFeedbackRepository,
            user_service: UserService,
    ):
        self.feedback_repository = feedback_repository
        self.user_service = user_service

    async def create_feedback(
            self,
            user_id: UUID,
            message: str,
            type: FeedbackType,
            form_filled_time_ms: int,
    ):
        logger.info(
            "Attempting to create feedback: user_id=%s, type=%s, form_filled_time_ms=%d",
            user_id,
            type,
            form_filled_time_ms,
        )

        self.validate_message(message, user_id)
        self.validate_form_filled_time_ms(form_filled_time_ms, user_id)

        feedback = Feedback(
            user_id=user_id,
            message=message,
            status=FeedbackStatus.CREATED,
            type=type,
            form_fill_time_ms=form_filled_time_ms,
        )

        try:
            await self.feedback_repository.create(feedback)
            logger.info(
                "Feedback successfully created: feedback_id=%s, user_id=%s, type=%s",
                feedback.id,
                user_id,
                type,
            )
        except Exception as e:
            logger.error(
                "Failed to create feedback in database: user_id=%s, error=%s",
                user_id,
                str(e),
            )
            raise e

        return feedback

    @staticmethod
    def validate_message(message: str, user_id: UUID | None = None):
        message = message.strip()
        if len(message) <= 0:
            logger.warning("Feedback validation failed: empty message for user_id=%s", user_id)
            raise BusinessLogicException(
                FeedbackErrorCodes.FEEDBACK_MESSAGE_IS_INVALID.value,
                "Feedback message is invalid, it must not be empty",
            )

    @staticmethod
    def validate_form_filled_time_ms(ms: int, user_id: UUID | None = None):
        if ms <= 0:
            logger.warning(
                "Feedback validation failed: invalid form_filled_time_ms=%d for user_id=%s",
                ms,
                user_id,
            )
            raise BusinessLogicException(
                BaseErrorCodes.INVALID_FORM_FILLED_TIME.value,
                "Form filled time is invalid, it must be positive",
            )
