from abc import ABC, abstractmethod
from typing import List
from uuid import UUID

from api.v1.schemas.responses.decks import DeckSimpleView, DeckDetailedView, DeckWithStatsView
from api.v1.utils.pagination import Pagination


class IDeckService(ABC):
    @abstractmethod
    async def get_decks_for_user(
        self, 
        actor_id: UUID, 
        offset: int = 0,
        limit: int = 50
        ) -> List[DeckSimpleView]:
        """
        Returns a page-by-page list of decks for the specified user.

        Args:
            actor_id: The ID of the user whose decks are being requested.
            offset: Number of entries to skip (for pagination).
            limit: The maximum number of decks to be returned.

        Returns:
            tuple[DeckSimpleView, ...]: A tuple of simplified deck views.
        """
        pass

    @abstractmethod
    async def get_paginated_decks_for_user(
        self,
        actor_id: UUID,
        name: str | None = None,
        page: int = 1,
    ) -> tuple[list[DeckWithStatsView], Pagination]:
        """
        Returns paginated list of user's decks.

        Args:
            actor_id: ID of the user whose decks are requested.
            page: Page number (starts from 1).
            name: Optional name filter for decks (case-insensitive, partial match).

        Returns:
            DecksListResponse: List of decks with pagination metadata.
        """
        pass

    @abstractmethod
    async def create_deck(
        self,
        actor_id: UUID,
        name: str,
        desc: str,
        is_public: bool = False,
    ) -> DeckSimpleView:
        """
        Creates a new deck.

        Args:
            actor_id: ID of the user creating the deck.
            name: Deck title (must not be empty).
            desc: Deck description.
            is_public: Public visibility flag (defaults to False).

        Returns:
            DeckSimpleView: Simplified representation of the created deck.
        """
        pass

    @abstractmethod
    async def update_deck(
        self,
        actor_id: UUID,
        deck_id: UUID,
        new_name: str | None = None,
        new_desc: str | None = None,
        is_public: bool | None = None,
    ) -> DeckSimpleView:
        """
        Partially updates deck fields.
        Fields passed as None remain unchanged.

        Args:
            actor_id: ID of the user performing the update.
            deck_id: ID of the deck to update.
            new_name: New deck title (optional).
            new_desc: New deck description (optional).
            is_public: New public visibility flag (optional).

        Returns:
            DeckSimpleView: Simplified representation of the updated deck.
        """
        pass

    @abstractmethod
    async def delete_deck(
        self,
        actor_id: UUID,
        deck_id: UUID,
    ) -> DeckSimpleView:
        """
        Deletes (or archives) a deck.
        Implementation determines the behavior: physical deletion or soft-delete.
        Throws NotFoundException or PermissionDeniedException if necessary.

        Args:
            actor_id: ID of the user performing the deletion.
            deck_id: ID of the deck to delete.

        Returns:
            DeckSimpleView: Simplified representation of the deleted deck.
        """
        pass

    @abstractmethod
    async def get_deck_details(
        self,
        actor_id: UUID,
        deck_id: UUID,
    ) -> DeckDetailedView:
        """
        Returns detailed information about a deck, including timestamps.
        Checks user access permissions if necessary.

        Args:
            actor_id: ID of the user requesting the data.
            deck_id: ID of the requested deck.

        Returns:
            DeckDetailedView: Complete representation of the deck with created_at and updated_at fields.
        """
        pass

    @abstractmethod
    async def get_recently_studied_decks(self, actor_id: UUID) -> list[DeckSimpleView]:
        """Returns recently studied decks for the user ordered by latest review timestamp."""
        pass

    @abstractmethod
    async def get_paginated_active_decks_for_user(
            self,
            actor_id: UUID,
            page: int = 1,
    ) -> tuple[list[DeckWithStatsView], Pagination]:
        """Returns paginated active user decks (cards_to_learn > 0) with aggregate metrics."""
        pass

