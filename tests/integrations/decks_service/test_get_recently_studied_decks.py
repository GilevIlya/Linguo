from datetime import datetime, timedelta, timezone

from api.v1.models import Card, CardReview
from api.v1.services.decks_service import DecksService


async def _create_card_with_review(session, deck_id, reviewed_at: datetime | None) -> None:
    card = Card(
        term="term",
        definition="definition",
        deck_id=deck_id,
        additional_fields=[],
    )
    session.add(card)
    await session.flush()

    review = CardReview(
        card_id=card.id,
        last_review=reviewed_at,
    )
    session.add(review)
    await session.commit()


class TestGetRecentlyStudiedDecks:
    async def test_returns_three_unique_decks_sorted_by_latest_review(
        self,
        decks_service: DecksService,
        session,
        new_user,
    ):
        deck_1 = await decks_service.create_deck(actor_id=new_user.id, name="Deck 1", desc="D1")
        deck_2 = await decks_service.create_deck(actor_id=new_user.id, name="Deck 2", desc="D2")
        deck_3 = await decks_service.create_deck(actor_id=new_user.id, name="Deck 3", desc="D3")
        deck_4 = await decks_service.create_deck(actor_id=new_user.id, name="Deck 4", desc="D4")

        now = datetime.now(timezone.utc)
        await _create_card_with_review(session, deck_1.id_, now - timedelta(days=2))
        await _create_card_with_review(session, deck_2.id_, now - timedelta(hours=12))
        await _create_card_with_review(session, deck_2.id_, now - timedelta(hours=3))
        await _create_card_with_review(session, deck_3.id_, now - timedelta(days=4))
        await _create_card_with_review(session, deck_4.id_, now - timedelta(hours=1))

        recent_decks = await decks_service.get_recently_studied_decks(actor_id=new_user.id)

        assert len(recent_decks) == 3
        assert [deck.id_ for deck in recent_decks] == [deck_4.id_, deck_2.id_, deck_1.id_]

    async def test_returns_empty_list_when_user_has_no_reviews(
        self,
        decks_service: DecksService,
        new_user,
    ):
        await decks_service.create_deck(actor_id=new_user.id, name="No reviews deck", desc="-")

        recent_decks = await decks_service.get_recently_studied_decks(actor_id=new_user.id)

        assert recent_decks == []

    async def test_excludes_decks_of_other_users(
        self,
        decks_service: DecksService,
        session,
        new_user,
        create_user,
        user_service,
    ):
        another_user = await user_service.create_user(create_user())

        own_deck = await decks_service.create_deck(actor_id=new_user.id, name="Own deck", desc="-")
        foreign_deck = await decks_service.create_deck(actor_id=another_user.id, name="Foreign deck", desc="-")

        now = datetime.now(timezone.utc)
        await _create_card_with_review(session, own_deck.id_, now - timedelta(minutes=10))
        await _create_card_with_review(session, foreign_deck.id_, now)

        recent_decks = await decks_service.get_recently_studied_decks(actor_id=new_user.id)

        assert len(recent_decks) == 1
        assert recent_decks[0].id_ == own_deck.id_

