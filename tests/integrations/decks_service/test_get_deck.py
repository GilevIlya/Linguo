import uuid
from datetime import datetime, timedelta, timezone

import pytest

from api.v1.models import Card, CardReview
from api.v1.services.decks_service import DecksService
from api.v1.services.exceptions.base_exceptions import PermissionDeniedException, ValidationException


class TestGetDeckDetails:
    """GET_DECK_DETAILS — успешное получение своей колоды"""
    async def test_get_own_deck_details(self, decks_service: DecksService, new_user, create_deck):
        deck = create_deck(new_user.id)
        created = await decks_service.create_deck(
            actor_id=new_user.id,
            name=deck.name,
            desc=deck.description
        )

        details = await decks_service.get_deck_details(actor_id=new_user.id, deck_id=created.id_)
        assert details.id_ == created.id_
        assert details.title == deck.name
        assert details.description == deck.description

    """GET_DECK_DETAILS — приватная колода другого юзера → PermissionDenied"""
    async def test_get_private_deck_of_another_user_denied(self, decks_service: DecksService, new_user, create_deck):
        deck = create_deck(new_user.id)
        created = await decks_service.create_deck(
            actor_id=new_user.id,
            name=deck.name,
            desc=deck.description
        )

        with pytest.raises(PermissionDeniedException):
            await decks_service.get_deck_details(actor_id=uuid.uuid4(), deck_id=created.id_)

    """GET_DECK_DETAILS — публичная колода другого юзера → доступ разрешён"""
    async def test_get_public_deck_of_another_user_allowed(self, decks_service: DecksService, new_user, create_deck):
        deck = create_deck(new_user.id)
        created = await decks_service.create_deck(
            actor_id=new_user.id,
            name=deck.name,
            desc=deck.description,
            is_public=True
        )

        details = await decks_service.get_deck_details(actor_id=uuid.uuid4(), deck_id=created.id_)
        assert details.id_ == created.id_
        assert details.title == deck.name
        assert details.description == deck.description


    async def test_get_all_decks_for_user(self, decks_service: DecksService, new_user, create_deck):
        decks = [await decks_service.create_deck(actor_id=new_user.id, name=f"Deck {i}", desc=f"Desc {i}") for i in
                 range(3)]

        result = await decks_service.get_decks_for_user(actor_id=new_user.id)
        assert len(result) == 3
        titles = [d.title for d in result]
        assert all(f"Deck {i}" in titles for i in range(3))

    """GET_DECKS_FOR_USER — пагинация offset/limit"""
    async def test_get_decks_pagination(self, decks_service: DecksService, new_user, create_deck):
        for i in range(5):
            await decks_service.create_deck(actor_id=new_user.id, name=f"Deck {i}", desc=f"Desc {i}")

        first_two = await decks_service.get_decks_for_user(actor_id=new_user.id, offset=0, limit=2)
        assert len(first_two) == 2

        next_two = await decks_service.get_decks_for_user(actor_id=new_user.id, offset=2, limit=2)
        assert len(next_two) == 2

    """GET_DECKS_FOR_USER — отрицательные offset/limit → ValidationException"""
    async def test_get_decks_invalid_pagination(self, decks_service: DecksService, new_user):
        with pytest.raises(ValidationException):
            await decks_service.get_decks_for_user(actor_id=new_user.id, offset=-1)

        with pytest.raises(ValidationException):
            await decks_service.get_decks_for_user(actor_id=new_user.id, limit=-5)


class TestGetPaginatedDecksForUser:
    async def test_returns_decks_with_total_cards_and_cards_to_learn(
        self,
        decks_service: DecksService,
        session,
        new_user,
    ):
        deck_1 = await decks_service.create_deck(actor_id=new_user.id, name="Deck A", desc="A")
        deck_2 = await decks_service.create_deck(actor_id=new_user.id, name="Deck B", desc="B")

        now = datetime.now(timezone.utc)

        card_1 = Card(term="t1", definition="d1", deck_id=deck_1.id_, additional_fields=[])
        card_2 = Card(term="t2", definition="d2", deck_id=deck_1.id_, additional_fields=[])
        card_3 = Card(term="t3", definition="d3", deck_id=deck_2.id_, additional_fields=[])
        session.add_all([card_1, card_2, card_3])
        await session.flush()

        session.add_all([
            CardReview(card_id=card_1.id, due=now - timedelta(hours=1)),
            CardReview(card_id=card_2.id, due=now + timedelta(hours=2)),
            CardReview(card_id=card_3.id, due=now - timedelta(hours=3)),
        ])
        await session.commit()

        decks, _ = await decks_service.get_paginated_decks_for_user(actor_id=new_user.id, page=1)

        mapped = {deck.id_: deck for deck in decks}

        assert mapped[deck_1.id_].total_cards == 2
        assert mapped[deck_1.id_].cards_to_learn == 1
        assert mapped[deck_2.id_].total_cards == 1
        assert mapped[deck_2.id_].cards_to_learn == 1
