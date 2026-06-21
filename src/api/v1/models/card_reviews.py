from datetime import datetime, timezone
from enum import IntEnum
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, Float, ForeignKey, Integer, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .basemodel import BaseModel
from .mixins.id_mixins import UUIDMixin

if TYPE_CHECKING:
    from .cards import Card

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


class CardState(IntEnum):
    """
    Enum representing the state of a card:
    - LEARNING: The card is in the learning phase.
    - REVIEW: The card is in the review phase.
    - RELEARNING: The card is being relearned.
    """

    LEARNING = 1
    REVIEW = 2
    RELEARNING = 3


class CardReview(BaseModel, UUIDMixin):
    """
    Model representing a review session for a card.

    Attributes:
        card_id: UUID of the associated card.
        due: Datetime when the card is due for review.
        last_review: Datetime of the last review (optional).
        state: Current state of the card (uses CardState enum, optional).
        step: Current step in the review process (optional).
        stability: Stability score of the card (optional).
        difficulty: Difficulty score of the card (optional).
        reps: Number of repetitions completed for the card.
        lapses: Number of times the card was forgotten.
        card: Relationship to the associated Card model.
    """

    __tablename__ = "card_reviews"

    card_id: Mapped[UUID] = mapped_column(
        ForeignKey("cards.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    due: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )
    last_review: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        default=None,
    )
    state: Mapped[CardState | None] = mapped_column(
        SmallInteger,
        default=None,
    )
    step: Mapped[int | None] = mapped_column(
        Integer,
        default=None,
    )
    stability: Mapped[float | None] = mapped_column(
        Float,
        default=None,
    )
    difficulty: Mapped[float | None] = mapped_column(
        Float,
        default=None,
    )

    card: Mapped["Card"] = relationship(
        "Card",
        lazy="noload",
    )

    def to_dict(self):
        return {
        "card_id": self.card_id,
        "due": self.due,
        "last_review": self.last_review,
        "state": self.state,
        "step": self.step,
        "stability": self.stability,
        "difficulty": self.difficulty,
    }
