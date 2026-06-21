from abc import abstractmethod
from uuid import UUID

from api.v1.models import CardReview
from api.v1.repositories.interfaces.IBaseRepository import IBaseRepository


class ICardReviewsRepository(IBaseRepository[CardReview, UUID]):

    @abstractmethod
    async def get_most_overdue_card(self, deck_id: UUID) -> CardReview | None:
        """Returns the most overdue card for review in the specified deck.

        Args:
            deck_id (UUID): The unique identifier of the deck.

        Returns:
            CardReview: The most overdue card review instance.
            None: if card review with expired due was not found.
        """
        pass

    @abstractmethod
    async def count_expired_reviews_by_deck(self, deck_id: UUID) -> int:
        """Counts the number of expired card reviews in the specified deck.

        Args:
            deck_id (UUID): The unique identifier of the deck.

        Returns:
            int: The number of expired card reviews.
        """
        pass

    @abstractmethod
    async def get_for_user(self, user_id: UUID, card_review_id: UUID) -> CardReview | None:
        """Returns the card review instance for the specified user.
        Args:
            card_review_id (UUID): The unique identifier of the card review.
            user_id(UUID): The unique identifier of the user.

        Returns:
            CardReview: The card review instance.
            None: if card review was not found or doesn't belong to the user.
        """
    pass

    @abstractmethod
    async def get_by_card_id(self, card_id: UUID) -> CardReview | None:
        """Returns a list of card reviews for the specified card.

        Args:
            card_id (UUID): The unique identifier of the card.

        Returns:
            CardReview: The card review instance.
            None: if card review was not found.
        """
        pass

    @abstractmethod
    async def count_untouched_cards_by_deck_id(self, deck_id: UUID) -> int:
        """Counts the number of untouched cards in the specified deck.
        Args:
            deck_id (UUID): The unique identifier of the deck.

        Returns:
            int: The number of untouched cards.
        """
        pass
