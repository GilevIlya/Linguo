import uuid
from io import BytesIO
from unittest.mock import AsyncMock

import pytest

from api.v1.services.card_service import CardService
from api.v1.services.exceptions.base_exceptions import (
    NotFoundException,
    BusinessLogicException,
)
from api.v1.services.exceptions.error_codes.card_error_codes import CardErrorCodes
from api.v1.services.schemas.file_param import FileParam


class TestUpdateCardIntegration:

    async def test_update_card_term_only(
        self, card_service: CardService, make_user, make_deck
    ):
        """Updating only the term persists the new value; definition is unchanged."""
        user = await make_user()
        deck = await make_deck(user_id=user.id)
        card = await card_service.create_card(
            actor_id=user.id, term="apple", def_="яблоко", deck_id=deck.id
        )

        result = await card_service.update_card(
            actor_id=user.id, card_id=card.id_, term="pear"
        )

        assert result.term == "pear"
        assert result.def_ == "яблоко"

    async def test_update_card_definition_only(
        self, card_service: CardService, make_user, make_deck
    ):
        """Updating only the definition persists the new value; term is unchanged."""
        user = await make_user()
        deck = await make_deck(user_id=user.id)
        card = await card_service.create_card(
            actor_id=user.id, term="apple", def_="яблоко", deck_id=deck.id
        )

        result = await card_service.update_card(
            actor_id=user.id, card_id=card.id_, def_="груша"
        )

        assert result.term == "apple"
        assert result.def_ == "груша"

    async def test_update_card_both_term_and_definition(
        self, card_service: CardService, make_user, make_deck
    ):
        """Updating both term and definition persists both values."""
        user = await make_user()
        deck = await make_deck(user_id=user.id)
        card = await card_service.create_card(
            actor_id=user.id, term="apple", def_="яблоко", deck_id=deck.id
        )

        result = await card_service.update_card(
            actor_id=user.id, card_id=card.id_, term="pear", def_="груша"
        )

        assert result.term == "pear"
        assert result.def_ == "груша"

    async def test_update_card_with_context(
        self, card_service: CardService, make_user, make_deck
    ):
        """Adding context to an existing card persists the additional field."""
        user = await make_user()
        deck = await make_deck(user_id=user.id)
        card = await card_service.create_card(
            actor_id=user.id, term="run", def_="бежать", deck_id=deck.id
        )

        await card_service.update_card(
            actor_id=user.id, card_id=card.id_, context="He {{runs}} every morning."
        )

        details = await card_service.get_card_details(actor_id=user.id, card_id=card.id_)
        context_fields = [f for f in details.additional_fields if f.type_ == "CONTEXT"]
        assert len(context_fields) == 1
        assert context_fields[0].content == "He {{runs}} every morning."

    async def test_update_card_with_image_replaces_old(
        self, card_service: CardService, make_user, make_deck, file_service_mock: AsyncMock
    ):
        """Uploading a new image replaces the old IMAGE additional field."""
        user = await make_user()
        deck = await make_deck(user_id=user.id)
        file_service_mock.upload_file.return_value = "image/old-key"
        image_old = FileParam(content=BytesIO(b"old"), content_type="image/png")
        card = await card_service.create_card(
            actor_id=user.id, term="cat", def_="кот", deck_id=deck.id, image=image_old
        )

        file_service_mock.upload_file.return_value = "image/new-key"
        image_new = FileParam(content=BytesIO(b"new"), content_type="image/jpeg")
        await card_service.update_card(
            actor_id=user.id, card_id=card.id_, image=image_new
        )

        details = await card_service.get_card_details(actor_id=user.id, card_id=card.id_)
        image_fields = [f for f in details.additional_fields if f.type_ == "IMAGE"]
        assert len(image_fields) == 1
        assert image_fields[0].content == "image/new-key"

    # ── Negative scenarios ────────────────────────────────────────────────

    async def test_update_card_not_found(self, card_service: CardService, make_user):
        """Updating a non-existent card raises NotFoundException."""
        user = await make_user()

        with pytest.raises(NotFoundException) as exc_info:
            await card_service.update_card(
                actor_id=user.id, card_id=uuid.uuid4(), term="new"
            )

        assert exc_info.value.error_code == CardErrorCodes.CARD_NOT_FOUND.value

    async def test_update_card_empty_term_raises_error(
        self, card_service: CardService, make_user, make_deck
    ):
        """Updating term to empty string raises BusinessLogicException."""
        user = await make_user()
        deck = await make_deck(user_id=user.id)
        card = await card_service.create_card(
            actor_id=user.id, term="apple", def_="яблоко", deck_id=deck.id
        )

        with pytest.raises(BusinessLogicException) as exc_info:
            await card_service.update_card(
                actor_id=user.id, card_id=card.id_, term=""
            )

        assert exc_info.value.error_code == CardErrorCodes.INVALID_FIELD.value

    async def test_update_card_empty_definition_raises_error(
        self, card_service: CardService, make_user, make_deck
    ):
        """Updating definition to empty string raises BusinessLogicException."""
        user = await make_user()
        deck = await make_deck(user_id=user.id)
        card = await card_service.create_card(
            actor_id=user.id, term="apple", def_="яблоко", deck_id=deck.id
        )

        with pytest.raises(BusinessLogicException) as exc_info:
            await card_service.update_card(
                actor_id=user.id, card_id=card.id_, def_="  "
            )

        assert exc_info.value.error_code == CardErrorCodes.INVALID_FIELD.value

