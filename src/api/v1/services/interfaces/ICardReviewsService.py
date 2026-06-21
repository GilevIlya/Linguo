from abc import ABC, abstractmethod
from uuid import UUID

from api.v1.models import CardReview


class ICardReviewsService(ABC):

    @abstractmethod
    async def count_expired_reviews_by_deck(self, actor_id: UUID, deck_id: UUID) -> int:
        """
        Counts the number of expired card reviews for a specific deck and actor.

        Args:
            actor_id (UUID): The unique identifier of the actor (user).
            deck_id (UUID): The unique identifier of the deck.

        Returns:
            int: The number of expired reviews for the given deck and actor.
        """
        pass

    @abstractmethod
    async def create_card_review(self, actor_id: UUID, card_id: UUID) -> CardReview:
        """Creates a new card review for the specified actor and card.

        Args:
            actor_id (UUID): Unique identifier of the actor (user).
            card_id (UUID): Unique identifier of the card.

        Returns:
            CardReview: The created card review instance.
        """
        pass

    @abstractmethod
    async def count_untouched_cards_by_deck(self, actor_id: UUID, deck_id: UUID) -> int:
        """Retrieves the number of untouched cards for a specific deck and actor.

        Args:
            actor_id (UUID): The unique identifier of the actor (user).
            deck_id (UUID): The unique identifier of the deck.

        Returns:
            int: The number of new card reviews for the given deck and actor.
        """
    pass
