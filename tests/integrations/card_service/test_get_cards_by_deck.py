import uuid
from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.repositories.card_repository import CardRepository
from api.v1.repositories.card_reviews_repository import CardReviewsRepository
from api.v1.repositories.deck_repository import DeckRepository
from api.v1.services.card_reviews_service import CardReviewsService
from api.v1.services.card_service import CardService
from api.v1.services.exceptions.base_exceptions import (
    NotFoundException,
    BusinessLogicException,
)
from api.v1.services.exceptions.error_codes.base import BaseErrorCodes
from api.v1.services.exceptions.error_codes.decks_error_codes import DeckErrorCodes
from api.v1.services.interfaces.IDeckService import IDeckService
from api.v1.services.interfaces.ISrsService import ISrsService
from api.v1.services.user_service import UserService


@pytest.fixture
def card_service(session: AsyncSession, file_service_mock: AsyncMock) -> CardService:
    card_repository = CardRepository(session)
    deck_repository = DeckRepository(session)
    card_reviews_repository = CardReviewsRepository(session)
    card_reviews_service = CardReviewsService(
        card_repository=card_repository,
        card_reviews_repository=card_reviews_repository,
        deck_repository=deck_repository,
    )

    return CardService(
        user_service=AsyncMock(spec=UserService),
        deck_service=AsyncMock(spec=IDeckService),
        file_service=file_service_mock,
        card_repository=card_repository,
        deck_repository=deck_repository,
        card_reviews_service=card_reviews_service,
        card_reviews_repository=card_reviews_repository,
        srs_service=AsyncMock(spec=ISrsService),
    )


class TestGetCardsByDeckIntegration:

    async def test_get_cards_by_deck_happy_path(
        self, card_service: CardService, make_user, make_deck
    ):
        """Returns all cards from the user's own deck."""
        user = await make_user()
        deck = await make_deck(user_id=user.id)
        for i in range(3):
            await card_service.create_card(
                actor_id=user.id, term=f"term{i}", def_=f"def{i}", deck_id=deck.id
            )

        result = await card_service.get_cards_by_deck(
            actor_id=user.id, deck_id=deck.id, limit=10, offset=0
        )

        assert len(result) == 3

    async def test_get_cards_by_deck_empty(
        self, card_service: CardService, make_user, make_deck
    ):
        """Empty deck returns empty list."""
        user = await make_user()
        deck = await make_deck(user_id=user.id)

        result = await card_service.get_cards_by_deck(
            actor_id=user.id, deck_id=deck.id, limit=10, offset=3
        )

        assert result == tuple()

    async def test_get_cards_by_deck_pagination_limit(
        self, card_service: CardService, make_user, make_deck
    ):
        """Limit restricts the number of returned cards."""
        user = await make_user()
        deck = await make_deck(user_id=user.id)
        for i in range(5):
            await card_service.create_card(
                actor_id=user.id, term=f"t{i}", def_=f"d{i}", deck_id=deck.id
            )

        result = await card_service.get_cards_by_deck(
            actor_id=user.id, deck_id=deck.id, limit=3, offset=0
        )

        assert len(result) == 3

    async def test_get_cards_by_deck_pagination_offset(
        self, card_service: CardService, make_user, make_deck
    ):
        """Offset skips the first N cards."""
        user = await make_user()
        deck = await make_deck(user_id=user.id)
        for i in range(5):
            await card_service.create_card(
                actor_id=user.id, term=f"t{i}", def_=f"d{i}", deck_id=deck.id
            )

        result = await card_service.get_cards_by_deck(
            actor_id=user.id, deck_id=deck.id, limit=10, offset=3
        )

        assert len(result) == 2

    async def test_get_cards_by_deck_offset_beyond_total(
        self, card_service: CardService, make_user, make_deck
    ):
        """Offset exceeding total cards returns empty list."""
        user = await make_user()
        deck = await make_deck(user_id=user.id)
        await card_service.create_card(
            actor_id=user.id, term="only", def_="one", deck_id=deck.id
        )

        result = await card_service.get_cards_by_deck(
            actor_id=user.id, deck_id=deck.id, limit=10, offset=100
        )

        assert result == tuple()

    # ── Negative scenarios ────────────────────────────────────────────────

    @pytest.mark.parametrize("limit,offset", [
        (-1, 0),
        (0, -1),
        (-5, -5),
    ])
    async def test_get_cards_by_deck_negative_pagination_raises_error(
        self, card_service: CardService, make_user, make_deck, limit, offset
    ):
        """Negative limit or offset raises BusinessLogicException."""
        user = await make_user()
        deck = await make_deck(user_id=user.id)

        with pytest.raises(BusinessLogicException) as exc_info:
            await card_service.get_cards_by_deck(
                actor_id=user.id, deck_id=deck.id, limit=limit, offset=offset
            )

        assert exc_info.value.error_code == BaseErrorCodes.INVALID_PAGINATION.value

    async def test_get_cards_by_deck_deck_not_found(
        self, card_service: CardService, make_user
    ):
        """Non-existent deck raises NotFoundException."""
        user = await make_user()

        with pytest.raises(NotFoundException) as exc_info:
            await card_service.get_cards_by_deck(
                actor_id=user.id, deck_id=uuid.uuid4(), limit=10, offset=0
            )

        assert exc_info.value.error_code == DeckErrorCodes.DECK_NOT_FOUND.value

    async def test_get_cards_by_deck_private_deck_another_user(
        self, card_service: CardService, make_user, make_deck
    ):
        """Private deck of another user is not accessible."""
        owner = await make_user(email="owner@list.com")
        other = await make_user(email="other@list.com")
        deck = await make_deck(user_id=owner.id, is_public=False)
        await card_service.create_card(
            actor_id=owner.id, term="word", def_="слово", deck_id=deck.id
        )

        with pytest.raises(NotFoundException) as exc_info:
            await card_service.get_cards_by_deck(
                actor_id=other.id, deck_id=deck.id, limit=10, offset=0
            )

        assert exc_info.value.error_code == DeckErrorCodes.DECK_NOT_FOUND.value

    async def test_get_cards_by_deck_public_deck_another_user(
        self, card_service: CardService, make_user, make_deck
    ):
        """Public deck of another user is accessible."""
        owner = await make_user(email="owner@pub-list.com")
        other = await make_user(email="other@pub-list.com")
        deck = await make_deck(user_id=owner.id, is_public=True)
        await card_service.create_card(
            actor_id=owner.id, term="open", def_="открытый", deck_id=deck.id
        )

        result = await card_service.get_cards_by_deck(
            actor_id=other.id, deck_id=deck.id, limit=10, offset=0
        )

        assert len(result) == 1

