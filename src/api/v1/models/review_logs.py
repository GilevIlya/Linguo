from datetime import datetime, timezone
from enum import IntEnum
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Integer, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column

from .basemodel import BaseModel
from .mixins.id_mixins import UUIDMixin


class ReviewRating(IntEnum):
    """
    Enum representing review ratings:
    - AGAIN: Indicates the review needs to be repeated.
    - HARD: Indicates the review was difficult.
    - GOOD: Indicates the review was satisfactory.
    - EASY: Indicates the review was easy.
    """

    AGAIN = 1
    HARD = 2
    GOOD = 3
    EASY = 4


class ReviewLog(BaseModel, UUIDMixin):
    """
    Model representing a log of card reviews.

    Attributes:
        review_id: UUID of the associated card review.
        rating: Rating given during the review (uses ReviewRating enum).
        review_datetime: Datetime when the review occurred.
        review_duration: Duration of the review in seconds.
    """

    __tablename__ = "review_logs"

    review_id: Mapped[UUID] = mapped_column(
        ForeignKey("card_reviews.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    rating: Mapped[ReviewRating] = mapped_column(
        SmallInteger
    )
    review_datetime: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )
    review_duration: Mapped[int] = mapped_column(
        Integer
    )
