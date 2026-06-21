import uuid
from unittest.mock import AsyncMock

import pytest

from api.v1.services.exceptions.base_exceptions import (
    NotFoundException,
)
from api.v1.services.exceptions.error_codes.card_error_codes import CardErrorCodes
from tests.card_service.helpers import _make_card


class TestDeleteCard:
    # DELETE_CARD_01
    async def test_delete_card_returns_simple_view_of_deleted_card(
        self, card_svc, card_repository: AsyncMock
    ):
        user_id = uuid.uuid4()
        card_id = uuid.uuid4()
        deck_id = uuid.uuid4()
        deleted_card = _make_card(card_id=card_id, deck_id=deck_id)
        card_repository.delete_if_owned_by.return_value = deleted_card

        result = await card_svc.delete_card(actor_id=user_id, id_=card_id)

        assert result.id_ == deleted_card.id
        assert result.term == deleted_card.term
        assert result.def_ == deleted_card.definition
        assert result.deck_id == deleted_card.deck_id

    async def test_delete_card_calls_repository_with_correct_args(
        self, card_svc, card_repository: AsyncMock
    ):
        user_id = uuid.uuid4()
        card_id = uuid.uuid4()
        card_repository.delete_if_owned_by.return_value = _make_card(card_id=card_id)

        await card_svc.delete_card(actor_id=user_id, id_=card_id)

        card_repository.delete_if_owned_by.assert_awaited_once_with(card_id, user_id)

    # DELETE_CARD_02
    async def test_delete_card_not_found_raises_not_found_exception(
        self, card_svc, card_repository: AsyncMock
    ):
        card_repository.delete_if_owned_by.return_value = None

        with pytest.raises(NotFoundException) as exc_info:
            await card_svc.delete_card(actor_id=uuid.uuid4(), id_=uuid.uuid4())

        assert exc_info.value.error_code == CardErrorCodes.CARD_NOT_FOUND.value

    # DELETE_CARD_04
    async def test_delete_already_deleted_card_raises_not_found_exception(
        self, card_svc, card_repository: AsyncMock
    ):
        # Soft-deleted cards are filtered out by the repository (returns None)
        card_repository.delete_if_owned_by.return_value = None

        with pytest.raises(NotFoundException) as exc_info:
            await card_svc.delete_card(actor_id=uuid.uuid4(), id_=uuid.uuid4())

        assert exc_info.value.error_code == CardErrorCodes.CARD_NOT_FOUND.value
