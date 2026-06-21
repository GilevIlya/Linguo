import uuid
from enum import StrEnum

from sqlalchemy import ForeignKey, CheckConstraint, Enum
from sqlalchemy.orm import mapped_column, Mapped

from . import BaseModel
from .mixins.id_mixins import UUIDMixin


class FeedbackStatus(StrEnum):
    CREATED = "CREATED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    REJECTED = "REJECTED"


class FeedbackType(StrEnum):
    BUG = "BUG"
    WISH = "WISH"
    OTHER = "OTHER"


class Feedback(BaseModel, UUIDMixin):
    __tablename__ = "feedbacks"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="NO ACTION"),
        index=True,
    )
    message: Mapped[str]
    status: Mapped[FeedbackStatus] = mapped_column(
        Enum(
            FeedbackStatus,
            name="feedback_status",
        ),
    )
    type: Mapped[FeedbackType] = mapped_column(
        Enum(
            FeedbackType,
            name="feedback_type",
        ),
        default=FeedbackType.OTHER
    )
    form_fill_time_ms: Mapped[int] = mapped_column(index=True)

    __table_args__ = (
        CheckConstraint("form_fill_time_ms >= 1"),
    )
