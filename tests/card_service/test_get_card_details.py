import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest

from api.v1.models.types.additional_fields import AdditionalField, AdditionalFieldType
from api.v1.services.exceptions.base_exceptions import (
    NotFoundException,
)
from api.v1.services.exceptions.error_codes.card_error_codes import CardErrorCodes
from tests.card_service.helpers import _make_card


class TestGetCardDetails:
    # GET_DETAILS_01
    async def test_get_card_details_returns_detailed_view_with_all_fields(
        self, card_svc, card_repository: AsyncMock
    ):
        user_id = uuid.uuid4()
        card_id = uuid.uuid4()
        deck_id = uuid.uuid4()
        now = datetime.now(timezone.utc)
        card = _make_card(
            card_id=card_id,
            deck_id=deck_id,
            additional_fields=[
                AdditionalField(type=AdditionalFieldType.IMAGE, content="image/key"),
                AdditionalField(type=AdditionalFieldType.CONTEXT, content="{{example}} context"),
            ],
            created_at=now,
            updated_at=now,
        )
        card_repository.get_owned_by_user.return_value = card

        result = await card_svc.get_card_details(actor_id=user_id, card_id=card_id)

        assert result.id_ == card_id
        assert result.term == card.term
        assert result.def_ == card.definition
        assert result.deck_id == deck_id
        assert len(result.additional_fields) == 2
        assert result.created_at == now
        assert result.updated_at == now

    # GET_DETAILS_02
    async def test_get_card_details_no_additional_fields_returns_empty_tuple(
        self, card_svc, card_repository: AsyncMock
    ):
        card_repository.get_owned_by_user.return_value = _make_card(additional_fields=[])

        result = await card_svc.get_card_details(actor_id=uuid.uuid4(), card_id=uuid.uuid4())

        assert result.additional_fields == ()

    # GET_DETAILS_03
    async def test_get_card_details_card_not_found_raises_not_found_exception(
        self, card_svc, card_repository: AsyncMock
    ):
        card_repository.get_owned_by_user.return_value = None

        with pytest.raises(NotFoundException) as exc_info:
            await card_svc.get_card_details(actor_id=uuid.uuid4(), card_id=uuid.uuid4())

        assert exc_info.value.error_code == CardErrorCodes.CARD_NOT_FOUND.value
