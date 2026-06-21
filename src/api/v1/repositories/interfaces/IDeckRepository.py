from abc import abstractmethod
from typing import Any, NamedTuple
from uuid import UUID

from api.v1.models.decks import Deck
from api.v1.repositories.interfaces.IBaseRepository import IBaseRepository


class IDeckRepository(IBaseRepository[Deck, UUID]):
    @abstractmethod
    async def find_by_user_id(
        self,
        user_id: UUID,
        limit: int = 50,
        offset: int = 0) -> list[Deck]:
        """
        Finds all decks associated with a specific user ID.

        Args:
            user_id (UUID): The ID of the user to search for.
            limit (int): The maximum number of decks to return.
            offset (int): The number of decks to skip before returning results.

        Returns:
            list[Deck]: A list of Deck objects associated with the given user ID.
        """
        pass

    @abstractmethod
    async def update(self, obj: Deck, data: dict[str, Any]) -> Deck:
        """
        Updates the given Deck object with the provided data.

        Args:
            obj (Deck): The Deck object to be updated.
            data (dict[str, Any]): A dictionary containing the fields to update and their new values.

        Returns:
            Deck: The updated Deck object after applying the changes.
        """
        pass

    @abstractmethod
    async def soft_delete(self, obj: Deck) -> Deck:
        """
        Performs a soft delete on the given Deck object.

        Args:
            obj (Deck): The Deck object to be soft deleted.

        Returns:
            Deck: The Deck object after being marked as deleted.
        """
        pass

    @abstractmethod
    async def find_recently_studied_by_user_id(self, user_id: UUID, limit: int = 3) -> list[Deck]:
        """Returns unique decks ordered by latest review activity for a user."""
        pass

    @abstractmethod
    async def find_by_user_id_with_stats(
        self,
        user_id: UUID,
        name: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list["ActiveDeckMetrics"]:
        """Returns user decks with total cards and due cards counters."""
        pass

    @abstractmethod
    async def find_active_by_user_id_with_metrics(
        self,
        user_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> list["ActiveDeckMetrics"]:
        """Returns active user decks (cards_to_learn > 0) with aggregate metrics."""
        pass


class ActiveDeckMetrics(NamedTuple):
    deck: Deck
    total_cards: int
    cards_to_learn: int


