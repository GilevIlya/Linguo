import pytest
import uuid

from api.v1.models import Deck
from api.v1.services.decks_service import DecksService

@pytest.fixture
async def decks_service(session):
    from api.v1.repositories.deck_repository import DeckRepository
    return DecksService(DeckRepository(session))

@pytest.fixture
def create_deck():
    counter = 0
    def _make(user_id: uuid.UUID):
        nonlocal counter
        counter += 1
        return Deck(
            user_id=user_id,
            name=f"Deck {counter}",
            description=f"Description for Deck {counter}",
            is_public=False
        )
    return _make