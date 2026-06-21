import uuid

import pytest

from api.v1.services.card_service import CardService
from api.v1.services.exceptions.base_exceptions import NotFoundException
from api.v1.services.exceptions.error_codes.card_error_codes import CardErrorCodes
from api.v1.services.exceptions.error_codes.decks_error_codes import DeckErrorCodes


class TestChangeCardDeckIntegration:

    async def test_change_card_deck_happy_path(
        self, card_service: CardService, make_user, make_deck
    ):
        """Card is successfully moved to another deck owned by the same user."""
        # Arrange
        user = await make_user()
        deck_a = await make_deck(user_id=user.id, name="Deck A")
        deck_b = await make_deck(user_id=user.id, name="Deck B")
        card = await card_service.create_card(
            actor_id=user.id, term="apple", def_="яблоко", deck_id=deck_a.id
        )

        # Act
        result = await card_service.change_card_deck(
            actor_id=user.id, card_id=card.id_, new_deck_id=deck_b.id
        )

        # Assert
        assert result.deck_id == deck_b.id

    async def test_change_card_deck_persisted_in_db(
        self, card_service: CardService, make_user, make_deck
    ):
        """After changing deck, get_card_details reflects the new deck_id."""
        user = await make_user()
        deck_a = await make_deck(user_id=user.id, name="Deck A")
        deck_b = await make_deck(user_id=user.id, name="Deck B")
        card = await card_service.create_card(
            actor_id=user.id, term="cat", def_="кот", deck_id=deck_a.id
        )

        await card_service.change_card_deck(
            actor_id=user.id, card_id=card.id_, new_deck_id=deck_b.id
        )

        details = await card_service.get_card_details(actor_id=user.id, card_id=card.id_)
        assert details.deck_id == deck_b.id

    # ── Negative scenarios ────────────────────────────────────────────────

    async def test_change_card_deck_card_not_found(
        self, card_service: CardService, make_user, make_deck
    ):
        """Non-existent card raises NotFoundException."""
        user = await make_user()
        deck = await make_deck(user_id=user.id)

        with pytest.raises(NotFoundException) as exc_info:
            await card_service.change_card_deck(
                actor_id=user.id, card_id=uuid.uuid4(), new_deck_id=deck.id
            )

        assert exc_info.value.error_code == CardErrorCodes.CARD_NOT_FOUND.value

    async def test_change_card_deck_target_deck_not_found(
        self, card_service: CardService, make_user, make_deck
    ):
        """Non-existent target deck raises NotFoundException."""
        user = await make_user()
        deck = await make_deck(user_id=user.id)
        card = await card_service.create_card(
            actor_id=user.id, term="apple", def_="яблоко", deck_id=deck.id
        )

        with pytest.raises(NotFoundException) as exc_info:
            await card_service.change_card_deck(
                actor_id=user.id, card_id=card.id_, new_deck_id=uuid.uuid4()
            )

        assert exc_info.value.error_code == DeckErrorCodes.DECK_NOT_FOUND.value

    async def test_change_card_deck_target_belongs_to_another_user(
        self, card_service: CardService, make_user, make_deck
    ):
        """Moving card to a deck owned by another user raises NotFoundException."""
        owner = await make_user(email="owner@change.com")
        other = await make_user(email="other@change.com")
        deck_owner = await make_deck(user_id=owner.id, name="Owner Deck")
        deck_other = await make_deck(user_id=other.id, name="Other Deck")
        card = await card_service.create_card(
            actor_id=owner.id, term="secret", def_="секрет", deck_id=deck_owner.id
        )

        with pytest.raises(NotFoundException) as exc_info:
            await card_service.change_card_deck(
                actor_id=owner.id, card_id=card.id_, new_deck_id=deck_other.id
            )

        assert exc_info.value.error_code == DeckErrorCodes.DECK_NOT_FOUND.value

