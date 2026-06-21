from abc import abstractmethod
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from api.v1.models.cards import Card
from api.v1.repositories.interfaces.IBaseRepository import IBaseRepository


@dataclass
class CardsWithStats:
    id_: UUID
    term: str
    def_: str
    deck_id: UUID
    next_review: datetime
    last_review: datetime | None
    created_at: datetime

class ICardRepository(IBaseRepository[Card, UUID]):
    @abstractmethod
    async def find_by_deck_id(
        self, 
        deck_id: UUID,
        limit: int = 50,
        offset: int = 0) -> list[Card]:
        """
        Finds all cards associated with a specific deck ID.

        Args:
            deck_id (UUID): The ID of the deck to search for.
            limit (int): The maximum number of cards to return.
            offset (int): The number of cards to skip before returning results.

        Returns:
            list[Card]: A list of Card objects associated with the given deck ID.
        """
        pass

    @abstractmethod
    async def find_by_deck_id_with_stats(
        self,
        deck_id: UUID,
        limit: int = 50,
        offset: int = 0,
        filter: str | None = None,
    ) -> list[CardsWithStats]:
        """
        Finds all cards associated with a specific deck ID, including review statistics for a specific user.

        Args:
            deck_id (UUID): The ID of the deck to search for.
            limit (int): The maximum number of cards to return.
            offset (int): The number of cards to skip before returning results.
            filter (str | None): Optional string to filter cards by term or definition (partial match).

        Returns:
            list[CardsWithStats]: A list of cards with statistics for the specified user.
        """
        pass

    @abstractmethod
    async def delete_if_owned_by(self, card_id: UUID, user_id: UUID) -> Card | None:
        """
        Soft-deletes a card by setting its `deleted_at` field if it is owned by the specified user.

        Args:
            card_id (UUID): The ID of the card to soft-delete.
            user_id (UUID): The ID of the user who must own the card for the operation to succeed.

        Returns:
            Card | None: The updated Card object with `deleted_at` set if the operation was successful,
            or None if the card was not found, already deleted, or not owned by the user.
        """
        pass

    @abstractmethod
    async def get_owned_by_user(self, card_id: UUID, user_id: UUID) -> Card | None:
        """
        Retrieves a card if it is owned by the specified user.

        Args:
            card_id (UUID): The ID of the card to retrieve.
            user_id (UUID): The ID of the user who must own the card for it to be retrieved.

        Returns:
            Card | None: The Card object if it is owned by the user, or None if the card was not found or not owned by the user.
        """
        pass

    @abstractmethod
    async def get_random_from_deck(self, deck_id: UUID, exclude_id: UUID, limit = 3) -> list[Card]:
        """
        Retrieves a random selection of cards from a specific deck, excluding a specified card.

        Args:
            deck_id (UUID): The ID of the deck to retrieve cards from.
            exclude_id (UUID): The ID of the card to exclude from the results.
            limit (int): The maximum number of cards to return.

        Returns:
            list[Card]: A list of Card objects associated with the given deck ID.
        """
        pass

    @abstractmethod
    async def count_by_deck(self, deck_id: UUID, filter: str | None) -> int:
        """
        Updates the deck association of a card.

        Args:
            deck_id: The ID of the deck to count cards in.
                filter: Optional string to filter cards by term and definition (partial match).

        Returns:
            int: The number of cards associated with the specified deck.
        """
        pass
