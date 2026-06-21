"""
Integration tests for CardService.delete_card

Scenarios covered:
  - Happy path: delete own card
  - Verify card is actually removed from the DB after deletion
  - Card not found → NotFoundException
  - Attempt to delete another user's card → NotFoundException (card_repository filters by ownership)
"""

import uuid

import pytest

from api.v1.services.card_service import CardService
from api.v1.services.exceptions.base_exceptions import NotFoundException
from api.v1.services.exceptions.error_codes.card_error_codes import CardErrorCodes


class TestDeleteCardIntegration:

    async def test_delete_card_happy_path(
        self, card_service: CardService, make_user, make_deck
    ):
        """Deleting own card returns a correct CardSimpleView."""
        # Arrange
        user = await make_user()
        deck = await make_deck(user_id=user.id)
        card = await card_service.create_card(
            actor_id=user.id, term="apple", def_="яблоко", deck_id=deck.id
        )

        # Act
        result = await card_service.delete_card(actor_id=user.id, id_=card.id_)

        # Assert
        assert result.id_ == card.id_
        assert result.term == "apple"
        assert result.def_ == "яблоко"

    async def test_delete_card_is_actually_removed_from_db(
        self, card_service: CardService, make_user, make_deck
    ):
        """After deletion, get_card_details raises NotFoundException."""
        user = await make_user()
        deck = await make_deck(user_id=user.id)
        card = await card_service.create_card(
            actor_id=user.id, term="cat", def_="кот", deck_id=deck.id
        )

        await card_service.delete_card(actor_id=user.id, id_=card.id_)

        with pytest.raises(NotFoundException):
            await card_service.get_card_details(actor_id=user.id, card_id=card.id_)

    async def test_delete_card_not_found(self, card_service: CardService, make_user):
        """Deleting a non-existent card raises NotFoundException."""
        user = await make_user()

        with pytest.raises(NotFoundException) as exc_info:
            await card_service.delete_card(actor_id=user.id, id_=uuid.uuid4())

        assert exc_info.value.error_code == CardErrorCodes.CARD_NOT_FOUND.value

    async def test_delete_card_of_another_user_raises_not_found(
        self, card_service: CardService, make_user, make_deck
    ):
        """Attempting to delete someone else's card raises NotFoundException (ownership filter)."""
        owner = await make_user(email="owner@del.com")
        other = await make_user(email="other@del.com")
        deck = await make_deck(user_id=owner.id)
        card = await card_service.create_card(
            actor_id=owner.id, term="secret", def_="секрет", deck_id=deck.id
        )

        with pytest.raises(NotFoundException) as exc_info:
            await card_service.delete_card(actor_id=other.id, id_=card.id_)

        assert exc_info.value.error_code == CardErrorCodes.CARD_NOT_FOUND.value

