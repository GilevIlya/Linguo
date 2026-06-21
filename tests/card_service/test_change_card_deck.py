import uuid
from unittest.mock import AsyncMock

import pytest

from api.v1.services.exceptions.base_exceptions import (
    NotFoundException,
)
from api.v1.services.exceptions.error_codes.card_error_codes import CardErrorCodes
from api.v1.services.exceptions.error_codes.decks_error_codes import DeckErrorCodes
from tests.card_service.helpers import _make_card, _make_deck


class TestChangeCardDeck:
    # CHANGE_DECK_01
    async def test_change_card_deck_returns_view_with_new_deck_id(
        self, card_svc, card_repository: AsyncMock, deck_repository: AsyncMock
    ):
        user_id = uuid.uuid4()
        card_id = uuid.uuid4()
        deck_1_id = uuid.uuid4()
        deck_2_id = uuid.uuid4()
        card = _make_card(card_id=card_id, deck_id=deck_1_id)
        card_repository.get_owned_by_user.return_value = card
        deck_repository.get_by_id.return_value = _make_deck(deck_id=deck_2_id, user_id=user_id)
        card_repository.update.return_value = _make_card(card_id=card_id, deck_id=deck_2_id)

        result = await card_svc.change_card_deck(
            actor_id=user_id, card_id=card_id, new_deck_id=deck_2_id
        )

        assert result.deck_id == deck_2_id

        card_repository.update.assert_awaited_once_with(card, {"deck_id": deck_2_id})

    # CHANGE_DECK_02
    async def test_change_card_deck_card_not_found_raises_not_found_exception(
        self, card_svc, card_repository: AsyncMock
    ):
        card_repository.get_owned_by_user.return_value = None

        with pytest.raises(NotFoundException) as exc_info:
            await card_svc.change_card_deck(
                actor_id=uuid.uuid4(), card_id=uuid.uuid4(), new_deck_id=uuid.uuid4()
            )

        assert exc_info.value.error_code == CardErrorCodes.CARD_NOT_FOUND.value

    # CHANGE_DECK_03
    async def test_change_card_deck_target_deck_not_found_raises_not_found_exception(
        self, card_svc, card_repository: AsyncMock, deck_repository: AsyncMock
    ):
        card_repository.get_owned_by_user.return_value = _make_card()
        deck_repository.get_by_id.return_value = None

        with pytest.raises(NotFoundException) as exc_info:
            await card_svc.change_card_deck(
                actor_id=uuid.uuid4(), card_id=uuid.uuid4(), new_deck_id=uuid.uuid4()
            )

        assert exc_info.value.error_code == DeckErrorCodes.DECK_NOT_FOUND.value

    # CHANGE_DECK_04
    async def test_change_card_deck_target_deck_of_another_user_raises_not_found(
        self, card_svc, card_repository: AsyncMock, deck_repository: AsyncMock
    ):
        user_id = uuid.uuid4()
        other_user_id = uuid.uuid4()
        card_id = uuid.uuid4()
        new_deck_id = uuid.uuid4()

        # Existing card owned by user
        card_repository.get_owned_by_user.return_value = _make_card(card_id=card_id, deck_id=uuid.uuid4())

        # Target deck exists but owned by *another* user
        deck_repository.get_by_id.return_value = _make_deck(deck_id=new_deck_id, user_id=other_user_id)

        with pytest.raises(NotFoundException) as exc_info:
            await card_svc.change_card_deck(
                actor_id=user_id, card_id=card_id, new_deck_id=new_deck_id
            )

        assert exc_info.value.error_code == DeckErrorCodes.DECK_NOT_FOUND.value

    # CHANGE_DECK_05
    async def test_change_card_deck_target_deck_private_and_of_another_user_raises_not_found(
        self, card_svc, card_repository: AsyncMock, deck_repository: AsyncMock
    ):
        """Явный security-тест: целевая колода существует, is_public=False, принадлежит другому
        пользователю — пользователь не должен иметь возможности «подбросить» карточки в чужую колоду."""
        user_id = uuid.uuid4()
        other_user_id = uuid.uuid4()
        card_id = uuid.uuid4()
        new_deck_id = uuid.uuid4()

        card_repository.get_owned_by_user.return_value = _make_card(card_id=card_id)
        # Приватная колода другого пользователя
        deck_repository.get_by_id.return_value = _make_deck(
            deck_id=new_deck_id, user_id=other_user_id, is_public=False
        )

        with pytest.raises(NotFoundException) as exc_info:
            await card_svc.change_card_deck(
                actor_id=user_id, card_id=card_id, new_deck_id=new_deck_id
            )

        assert exc_info.value.error_code == DeckErrorCodes.DECK_NOT_FOUND.value

    # CHANGE_DECK_06
    async def test_change_card_deck_to_same_deck_returns_view_without_error(
        self, card_svc, card_repository: AsyncMock, deck_repository: AsyncMock
    ):
        user_id = uuid.uuid4()
        card_id = uuid.uuid4()
        deck_id = uuid.uuid4()
        existing_card = _make_card(card_id=card_id, deck_id=deck_id)
        card_repository.get_owned_by_user.return_value = existing_card
        deck_repository.get_by_id.return_value = _make_deck(deck_id=deck_id, user_id=user_id)
        card_repository.update.return_value = existing_card

        result = await card_svc.change_card_deck(
            actor_id=user_id, card_id=card_id, new_deck_id=deck_id
        )

        assert result.deck_id == deck_id
