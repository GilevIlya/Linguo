import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest

from api.v1.repositories.interfaces.ICardRepository import CardsWithStats
from api.v1.services.exceptions.base_exceptions import (
    BusinessLogicException,
    NotFoundException,
)
from api.v1.services.exceptions.error_codes.base import BaseErrorCodes
from api.v1.services.exceptions.error_codes.decks_error_codes import DeckErrorCodes
from tests.card_service.helpers import _make_deck


def _make_card_with_stats(deck_id: uuid.UUID) -> CardsWithStats:
    return CardsWithStats(
        id_=uuid.uuid4(),
        term="apple",
        def_="яблоко",
        deck_id=deck_id,
        next_review=datetime.now(timezone.utc),
        last_review=None,
        created_at=datetime.now(timezone.utc),
    )


class TestGetCardsByDeck:
    # GET_BY_DECK_01
    async def test_get_cards_by_deck_returns_list_of_card_views(
        self, card_svc, card_repository: AsyncMock, deck_repository: AsyncMock
    ):
        user_id = uuid.uuid4()
        deck_id = uuid.uuid4()
        deck_repository.get_by_id.return_value = _make_deck(deck_id=deck_id, user_id=user_id)
        card_repository.find_by_deck_id_with_stats.return_value = [
            _make_card_with_stats(deck_id=deck_id) for _ in range(5)
        ]
        
        result = await card_svc.get_cards_by_deck(
            actor_id=user_id, deck_id=deck_id, limit=10, offset=0
        )
        

        assert len(result) == 5
        assert all(card.deck_id == deck_id for card in result)

    async def test_get_cards_by_deck_calls_repository_with_pagination_params(
        self, card_svc, card_repository: AsyncMock, deck_repository: AsyncMock
    ):
        user_id = uuid.uuid4()
        deck_id = uuid.uuid4()
        deck_repository.get_by_id.return_value = _make_deck(deck_id=deck_id, user_id=user_id)
        card_repository.find_by_deck_id_with_stats.return_value = tuple()

        await card_svc.get_cards_by_deck(
            actor_id=user_id, deck_id=deck_id, limit=5, offset=10
        )

        card_repository.find_by_deck_id_with_stats.assert_awaited_once_with(deck_id, 5, 10, None)

    # GET_BY_DECK_02
    async def test_get_cards_by_deck_empty_deck_returns_empty_list(
        self, card_svc, card_repository: AsyncMock, deck_repository: AsyncMock
    ):
        user_id = uuid.uuid4()
        deck_id = uuid.uuid4()
        deck_repository.get_by_id.return_value = _make_deck(deck_id=deck_id, user_id=user_id)
        card_repository.find_by_deck_id_with_stats.return_value = tuple()

        result = await card_svc.get_cards_by_deck(
            actor_id=user_id, deck_id=deck_id, limit=10, offset=0
        )

        assert result == tuple()

    # GET_BY_DECK_03
    async def test_get_cards_by_deck_offset_shifts_results(
        self, card_svc, card_repository: AsyncMock, deck_repository: AsyncMock
    ):
        user_id = uuid.uuid4()
        deck_id = uuid.uuid4()
        deck_repository.get_by_id.return_value = _make_deck(deck_id=deck_id, user_id=user_id)
        card_repository.find_by_deck_id_with_stats.return_value = [
            _make_card_with_stats(deck_id=deck_id) for _ in range(5)
        ]

        result = await card_svc.get_cards_by_deck(
            actor_id=user_id, deck_id=deck_id, limit=5, offset=5
        )

        card_repository.find_by_deck_id_with_stats.assert_awaited_once_with(deck_id, 5, 5, None)
        assert len(result) == 5

    # GET_BY_DECK_04
    async def test_get_cards_by_deck_offset_beyond_records_returns_empty_list(
        self, card_svc, card_repository: AsyncMock, deck_repository: AsyncMock
    ):
        user_id = uuid.uuid4()
        deck_id = uuid.uuid4()
        deck_repository.get_by_id.return_value = _make_deck(deck_id=deck_id, user_id=user_id)
        card_repository.find_by_deck_id_with_stats.return_value = tuple()

        result = await card_svc.get_cards_by_deck(
            actor_id=user_id, deck_id=deck_id, limit=10, offset=100
        )

        assert result == tuple()

    # GET_BY_DECK_05
    async def test_get_cards_by_deck_limit_zero_returns_empty_list(
        self, card_svc, card_repository: AsyncMock, deck_repository: AsyncMock
    ):
        """Spec: limit=0 should return an empty list without raising an error.

        NOTE: The current implementation raises BusinessLogicException for limit < 1.
        This test documents the expected spec behavior and will fail until the
        implementation is updated to treat limit=0 as a valid edge case.
        """
        user_id = uuid.uuid4()
        deck_id = uuid.uuid4()
        deck_repository.get_by_id.return_value = _make_deck(deck_id=deck_id, user_id=user_id)
        card_repository.find_by_deck_id_with_stats.return_value = tuple()

        result = await card_svc.get_cards_by_deck(
            actor_id=user_id, deck_id=deck_id, limit=0, offset=0
        )

        assert result == tuple()

    # GET_BY_DECK_06
    async def test_get_cards_by_deck_deck_not_found_raises_not_found_exception(
        self, card_svc, deck_repository: AsyncMock
    ):
        deck_repository.get_by_id.return_value = None

        with pytest.raises(NotFoundException) as exc_info:
            await card_svc.get_cards_by_deck(
                actor_id=uuid.uuid4(), deck_id=uuid.uuid4(), limit=10, offset=0
            )

        assert exc_info.value.error_code == DeckErrorCodes.DECK_NOT_FOUND.value

    # GET_BY_DECK_07
    async def test_get_cards_by_deck_returns_not_found_on_private_deck_of_another_user(
        self, card_svc, deck_repository: AsyncMock
    ):
        start_user_id = uuid.uuid4()
        other_user_id = uuid.uuid4()
        deck_id = uuid.uuid4()

        # Private deck owned by another user
        deck_repository.get_by_id.return_value = _make_deck(
            deck_id=deck_id, user_id=other_user_id, is_public=False
        )

        with pytest.raises(NotFoundException) as exc_info:
            # User attempts to access a private deck they don't own
            await card_svc.get_cards_by_deck(
                actor_id=start_user_id, deck_id=deck_id, limit=10, offset=0
            )

        assert exc_info.value.error_code == DeckErrorCodes.DECK_NOT_FOUND.value

    # GET_BY_DECK_08
    async def test_get_cards_by_deck_public_deck_of_another_user_returns_cards(
        self, card_svc, card_repository: AsyncMock, deck_repository: AsyncMock
    ):
        user_a = uuid.uuid4()
        deck_id = uuid.uuid4()
        public_deck = _make_deck(deck_id=deck_id, user_id=uuid.uuid4(), is_public=True)
        deck_repository.get_by_id.return_value = public_deck
        card_repository.find_by_deck_id_with_stats.return_value = [
            _make_card_with_stats(deck_id=deck_id) for _ in range(3)
        ]

        result = await card_svc.get_cards_by_deck(
            actor_id=user_a, deck_id=deck_id, limit=10, offset=0
        )

        assert len(result) == 3

    # GET_BY_DECK_09
    @pytest.mark.parametrize("limit,offset", [
        (-1, 0),
        (10, -5),
        (-1, -5),
    ])
    async def test_get_cards_by_deck_negative_pagination_raises_business_logic_exception(
        self, card_svc, limit: int, offset: int
    ):
        with pytest.raises(BusinessLogicException) as exc_info:
            await card_svc.get_cards_by_deck(
                actor_id=uuid.uuid4(), deck_id=uuid.uuid4(), limit=limit, offset=offset
            )

        assert exc_info.value.error_code == BaseErrorCodes.INVALID_PAGINATION.value
