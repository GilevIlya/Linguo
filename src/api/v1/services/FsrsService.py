import logging
import uuid
from datetime import datetime, timezone
from typing import override

from fsrs import Card, State, Scheduler, Rating, ReviewLog

from api.v1.configs.srs_config import srs_config
from api.v1.models.card_reviews import CardReview, ReviewRating, CardState
from api.v1.models.review_logs import ReviewLog as ReviewLogModel
from api.v1.services.interfaces.ISrsService import ISrsService
from api.v1.services.schemas.srs import ReviewResult

logger = logging.getLogger("app")

class FsrsService(ISrsService):
    def __init__(self, params: tuple[int, ...] | None = None): # TODO:/ придумать как пихать в Scheduler
        self.__scheduler = Scheduler(
            desired_retention=srs_config.DESIRED_RETENTION,
            learning_steps=srs_config.LEARNING_STEPS,
            relearning_steps=srs_config.RELEARNING_STEPS,
            maximum_interval=srs_config.MAX_INTERVAL,
            enable_fuzzing=srs_config.FUZZING,
        )

    @override
    def review_card(self, card_review: CardReview, rating: ReviewRating, review_time: datetime, review_duration: int) -> ReviewResult:
        logger.info("review card with id %s | review_rating: %d", card_review.card_id, rating.value)

        card = self._map_card_review_to_card(card_review)
        card, review = self.__scheduler.review_card(
            card,
            Rating(rating),
            review_datetime=review_time,
            review_duration=review_duration
        )

        logger.debug("card with id %s reviewed", uuid.UUID(int=card.card_id))

        return ReviewResult(
            card_review=self._map_card_to_review_card(card),
            review_log=self._map_review_to_review_log(card_review.id, review),
        )

    @override
    def get_card_retrievability(self, card_review: CardReview, curr_datetime: datetime | None = None) -> float:
        return self.__scheduler.get_card_retrievability(
            self._map_card_review_to_card(card_review),
            curr_datetime if curr_datetime else datetime.now(timezone.utc),
        )

    @staticmethod
    def _map_card_review_to_card(card_review: CardReview) -> Card:
        return Card(
            card_id=card_review.card_id.int,
            state=State(card_review.state if card_review.state else CardState.LEARNING),
            step=card_review.step,
            stability=card_review.stability,
            difficulty=card_review.difficulty,
            due=card_review.due,
            last_review=card_review.last_review,
        )

    @staticmethod
    def _map_card_to_review_card(card: Card) -> CardReview:
        return CardReview(
            card_id=uuid.UUID(int=card.card_id),
            state=CardState(card.state),
            step=card.step,
            stability=card.stability,
            difficulty=card.difficulty,
            due=card.due,
            last_review=card.last_review,
        )

    @staticmethod
    def _map_review_to_review_log(review_id: uuid.UUID, review: ReviewLog) -> ReviewLogModel:
        return ReviewLogModel(
            review_id=review_id,
            rating=ReviewRating(review.rating),
            review_datetime=review.review_datetime,
            review_duration=review.review_duration,
        )
