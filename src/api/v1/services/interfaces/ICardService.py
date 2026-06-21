from abc import ABC, abstractmethod
from uuid import UUID

from api.v1.schemas.responses.cards import CardSimpleView, CardDetailedView, CardDetailedViewWithStats, \
    CardSimpleViewWithStats
from api.v1.services.schemas.file_param import FileParam


class ICardService(ABC):
    """Interface (contract) for card management service."""

    @abstractmethod
    async def create_card(
            self,
            actor_id: UUID,
            term: str,
            def_: str,
            deck_id: UUID,
            sound: FileParam | None = None,
            image: FileParam | None = None,
            context: str | None = None,
            synonyms: tuple[str, ...] | None = None,
    ) -> CardSimpleView:
        """
        Creates a new card in the specified deck.

        Args:
            actor_id: ID of the user performing the action.
            term: The term/word.
            def_: Definition of the term.
            deck_id: ID of the target deck.
            sound: Optional audio file.
            image: Optional image.
            context: Optional usage example.
            synonyms: Optional list of synonyms.

        Returns:
            CardSimpleView: Simplified representation of the created card.
        """
        pass

    @abstractmethod
    async def delete_card(
            self,
            actor_id: UUID,
            id_: UUID,
    ) -> CardSimpleView:
        """
        Deletes a card by its ID.

        Args:
            actor_id: ID of the user performing the action.
            id_: ID of the card to delete.

        Returns:
            CardSimpleView: Simplified representation of the deleted card.
        """
        pass

    @abstractmethod
    async def update_card(
            self,
            actor_id: UUID,
            card_id: UUID,
            term: str | None = None,
            def_: str | None = None,
            sound: FileParam | None = None,
            image: FileParam | None = None,
            context: str | None = None,
            synonyms: tuple[str, ...] | None = None,
    ) -> CardDetailedView:
        """
        Updates an existing card's data.
        Fields passed as None remain unchanged.

        Args:
            actor_id: ID of the user performing the action.
            card_id: ID of the card to update.
            term: New term (if update needed).
            def_: New definition (if update needed).
            sound: Updated audio file.
            image: Updated image.
            context: Updated context.
            synonyms: Updated list of synonyms.

        Returns:
            CardDetailedView: Detailed representation of the updated card.
        """
        pass

    @abstractmethod
    async def change_card_deck(
            self,
            actor_id: UUID,
            card_id: UUID,
            new_deck_id: UUID,
    ) -> CardSimpleView:
        """
        Moves a card to another deck.

        Args:
            actor_id: ID of the user performing the action.
            card_id: ID of the card to move.
            new_deck_id: ID of the new target deck.

        Returns:
            CardSimpleView: Simplified representation of the card after moving.
        """
        pass

    @abstractmethod
    async def get_card_details(
            self,
            actor_id: UUID,
            card_id: UUID,
    ) -> CardDetailedViewWithStats:
        """
        Retrieves complete information about a card, including additional fields.

        Args:
            actor_id: ID of the user requesting the data.
            card_id: ID of the requested card.

        Returns:
            CardDetailedViewWithStats: Complete representation of the card with all additional fields.
        """
        pass

    @abstractmethod
    async def get_cards_by_deck(
            self,
            actor_id: UUID,
            deck_id: UUID,
            limit: int,
            offset: int,
            filter: str | None = None,
    ) -> tuple[CardSimpleViewWithStats, ...]:
        """
        Returns all cards from the specified deck.

        Args:
            actor_id: ID of the user requesting the data.
            deck_id: ID of the deck whose cards you want to get.
            offset: Number of entries to skip (for pagination).
            limit: The maximum number of entries to be returned.
            filter: Optional string to filter cards by term and definition (partial match).

        Returns:
            list[CardSimpleViewWithStats]: A list of simplified deck card representations with statistic.
        """
        pass

    @abstractmethod
    async def count_cards_in_deck(
            self,
            actor_id: UUID,
            deck_id: UUID,
            filter: str | None = None,
    ) -> int:
        """
        Counts the number of cards in the specified deck.

        Args:
            actor_id: ID of the user requesting the data.
            deck_id: ID of the deck to count cards in.
            filter: Optional string to filter cards by term and definition (partial match).

        Returns:
            int: Total number of cards in the deck.
        """
        pass
