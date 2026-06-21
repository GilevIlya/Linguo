from abc import ABC, abstractmethod
from datetime import datetime

from api.v1.models.card_reviews import ReviewRating, CardReview
from api.v1.services.schemas.srs import ReviewResult


# FSRS, SR2, ML,

class ISrsService(ABC):
    @abstractmethod
    def review_card(self, card_review: CardReview, rating: ReviewRating, review_time: datetime, review_duration: int) -> ReviewResult:
        """
        Reviews a card based on the provided rating.

        Args:
            card_review: CardReview object containing the current review state of the card.
            rating: ReviewRating indicating the quality of the review (e.g., Again, Hard, Good, Easy).
            review_time: ReviewTime indicating the time the review was made.
            review_duration: Duration of the review duration (milliseconds).

        Returns:
            ReviewResult containing the updated CardReview and the corresponding ReviewLog.
        """
        pass

    @abstractmethod
    def get_card_retrievability(self, card_review: CardReview, curr_datetime: datetime | None = None) -> float:
        """
        Calculates the retrievability of a card based on its review state.

        Args:
            card_review: CardReview object containing the current review state of the card.
            curr_datetime: datetime indicating the time the review was made (UTC).

        Returns:
            A float value representing the retrievability of the card (e.g., between 0 and 1).
        """
        pass
