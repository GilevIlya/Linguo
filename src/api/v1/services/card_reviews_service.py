from typing import override
from uuid import UUID

from api.v1.models import CardReview
from api.v1.repositories.interfaces.ICardRepository import ICardRepository
from api.v1.repositories.interfaces.ICardReviewsRepository import ICardReviewsRepository
from api.v1.repositories.interfaces.IDeckRepository import IDeckRepository
from api.v1.services.exceptions.base_exceptions import PermissionDeniedException, BusinessLogicException
from api.v1.services.exceptions.error_codes.base import BaseErrorCodes
from api.v1.services.exceptions.error_codes.quiz_error_codes import QuizErrorCodes
from api.v1.services.interfaces.ICardReviewsService import ICardReviewsService


class CardReviewsService(ICardReviewsService):
    def __init__(self, card_repository: ICardRepository, card_reviews_repository: ICardReviewsRepository, deck_repository: IDeckRepository):
        self.card_reviews_repository = card_reviews_repository
        self.deck_repository = deck_repository
        self.card_repository = card_repository


    @override
    async def count_expired_reviews_by_deck(self, actor_id: UUID, deck_id: UUID) -> int:
        deck = await self.deck_repository.get_by_id(deck_id)
        if deck is None:
            return 0

        if deck.user_id != actor_id:
            raise PermissionDeniedException(
                BaseErrorCodes.PERMISSION_DENIED.value,
                "You do not have permission to access this resource."
            )

        return await self.card_reviews_repository.count_expired_reviews_by_deck(deck_id)

    @override
    async def create_card_review(self, actor_id: UUID, card_id: UUID) -> CardReview:
        card = await self.card_repository.get_owned_by_user(card_id=card_id, user_id=actor_id)
        if card is None:
            raise BusinessLogicException(
                QuizErrorCodes.THERE_IS_NO_CARD_TO_REVIEW.value
            )

        review = CardReview(
            card_id=card_id,
        )

        return await self.card_reviews_repository.create(review)

    @override
    async def count_untouched_cards_by_deck(self, actor_id: UUID, deck_id: UUID) -> int:
        deck = await self.deck_repository.get_by_id(deck_id)
        if deck is None:
            return 0
        if deck.user_id != actor_id:
            raise PermissionDeniedException(
                BaseErrorCodes.PERMISSION_DENIED.value,
            )

        return await self.card_reviews_repository.count_untouched_cards_by_deck_id(deck_id)


