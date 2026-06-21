"""
Integration tests for CardService.get_card_details

Scenarios covered:
  - Happy path: retrieve card details with additional fields
  - Card with no additional fields → empty tuple
  - Card not found → NotFoundException
  - Another user cannot see card from a private deck → NotFoundException
"""

import uuid

import pytest

from api.v1.services.card_service import CardService
from api.v1.services.exceptions.base_exceptions import NotFoundException
from api.v1.services.exceptions.error_codes.card_error_codes import CardErrorCodes


class TestGetCardDetailsIntegration:

    async def test_get_card_details_happy_path(
        self, card_service: CardService, make_user, make_deck
    ):
        """Full card details are returned with correct fields."""
        user = await make_user()
        deck = await make_deck(user_id=user.id)
        card = await card_service.create_card(
            actor_id=user.id,
            term="apple",
            def_="яблоко",
            deck_id=deck.id,
            context="An {{apple}} a day.",
        )

        details = await card_service.get_card_details(actor_id=user.id, card_id=card.id_)

        assert details.id_ == card.id_
        assert details.term == "apple"
        assert details.def_ == "яблоко"
        assert details.deck_id == deck.id
        assert details.created_at is not None
        assert details.updated_at is not None
        context_fields = [f for f in details.additional_fields if f.type_ == "CONTEXT"]
        assert len(context_fields) == 1
        assert context_fields[0].content == "An {{apple}} a day."

    async def test_get_card_details_no_additional_fields(
        self, card_service: CardService, make_user, make_deck
    ):
        """Card without additional fields returns an empty tuple."""
        user = await make_user()
        deck = await make_deck(user_id=user.id)
        card = await card_service.create_card(
            actor_id=user.id, term="test", def_="тест", deck_id=deck.id
        )

        details = await card_service.get_card_details(actor_id=user.id, card_id=card.id_)

        assert details.additional_fields == ()

    async def test_get_card_details_not_found(self, card_service: CardService, make_user):
        """Non-existent card raises NotFoundException."""
        user = await make_user()

        with pytest.raises(NotFoundException) as exc_info:
            await card_service.get_card_details(actor_id=user.id, card_id=uuid.uuid4())

        assert exc_info.value.error_code == CardErrorCodes.CARD_NOT_FOUND.value

    async def test_get_card_details_private_deck_another_user(
        self, card_service: CardService, make_user, make_deck
    ):
        """Another user cannot retrieve card details from a private deck."""
        owner = await make_user(email="owner@details.com")
        other = await make_user(email="other@details.com")
        deck = await make_deck(user_id=owner.id, is_public=False)
        card = await card_service.create_card(
            actor_id=owner.id, term="secret", def_="секрет", deck_id=deck.id
        )

        with pytest.raises(NotFoundException) as exc_info:
            await card_service.get_card_details(actor_id=other.id, card_id=card.id_)

        assert exc_info.value.error_code == CardErrorCodes.CARD_NOT_FOUND.value

    async def test_get_card_details_public_deck_another_user_allowed(
        self, card_service: CardService, make_user, make_deck
    ):
        """Another user CAN retrieve card details from a public deck."""
        owner = await make_user(email="owner@pub.com")
        other = await make_user(email="other@pub.com")
        deck = await make_deck(user_id=owner.id, is_public=True)
        card = await card_service.create_card(
            actor_id=owner.id, term="open", def_="открытый", deck_id=deck.id
        )

        details = await card_service.get_card_details(actor_id=other.id, card_id=card.id_)

        assert details.id_ == card.id_
        assert details.term == "open"

