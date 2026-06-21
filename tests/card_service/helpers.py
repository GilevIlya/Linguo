import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock

from api.v1.models.cards import Card
from api.v1.models.decks import Deck


def _make_card(
    card_id: uuid.UUID | None = None,
    term: str = "apple",
    definition: str = "яблоко",
    deck_id: uuid.UUID | None = None,
    additional_fields: list | None = None,
    created_at: datetime | None = None,
    updated_at: datetime | None = None,
) -> MagicMock:
    """Creates a lightweight Card mock object for tests."""
    card = MagicMock(spec=Card)
    card.id = card_id or uuid.uuid4()
    card.term = term
    card.definition = definition
    card.deck_id = deck_id or uuid.uuid4()
    card.additional_fields = additional_fields if additional_fields is not None else []
    card.created_at = created_at or datetime.now(timezone.utc)
    card.updated_at = updated_at or datetime.now(timezone.utc)
    return card


def _make_deck(
    deck_id: uuid.UUID | None = None,
    user_id: uuid.UUID | None = None,
    is_public: bool = False,
    deleted_at: None = None
) -> MagicMock:
    """Creates a lightweight mock Deck object for tests."""
    deck = MagicMock(spec=Deck)
    deck.id = deck_id or uuid.uuid4()
    deck.user_id = user_id or uuid.uuid4()
    deck.is_public = is_public
    deck.deleted_at = deleted_at
    return deck