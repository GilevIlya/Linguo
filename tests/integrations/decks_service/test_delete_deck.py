import pytest
import uuid
from api.v1.services.decks_service import DecksService
from api.v1.services.exceptions.base_exceptions import NotFoundException, PermissionDeniedException

class TestDeckDelete:
    """DELETE_DECK_01 — Успешное удаление своей колоды"""
    async def test_delete_own_deck(self, decks_service: DecksService, new_user, create_deck):
        deck = create_deck(new_user.id)
        created = await decks_service.create_deck(
            actor_id=new_user.id,
            name=deck.name,
            desc=deck.description
        )

        deleted = await decks_service.delete_deck(actor_id=new_user.id, deck_id=created.id_)
        assert deleted.id_ == created.id_
        deck_from_db = await decks_service.deck_repository.get_by_id(created.id_)
        assert deck_from_db is not None
        assert deck_from_db.deleted_at is not None

    """DELETE_DECK_02 — Колода не найдена"""
    async def test_delete_nonexistent_deck_raises(self, decks_service: DecksService, new_user):
        fake_id = uuid.uuid4()
        with pytest.raises(NotFoundException):
            await decks_service.delete_deck(actor_id=new_user.id, deck_id=fake_id)

    """DELETE_DECK_03 — Колода принадлежит другому пользователю"""
    async def test_delete_other_users_deck_raises(self, decks_service: DecksService, new_user, create_deck):
        deck = create_deck(new_user.id)
        created = await decks_service.create_deck(
            actor_id=new_user.id,
            name=deck.name,
            desc=deck.description
        )

        with pytest.raises(PermissionDeniedException):
            await decks_service.delete_deck(actor_id=uuid.uuid4(), deck_id=created.id_)

    """DELETE_DECK_04 — Повторное удаление уже удалённой колоды"""
    async def test_delete_already_deleted_deck_raises(self, decks_service: DecksService, new_user, create_deck):
        deck = create_deck(new_user.id)
        created = await decks_service.create_deck(
            actor_id=new_user.id,
            name=deck.name,
            desc=deck.description
        )

        await decks_service.delete_deck(actor_id=new_user.id, deck_id=created.id_)

        with pytest.raises(NotFoundException):
            await decks_service.delete_deck(actor_id=new_user.id, deck_id=created.id_)

    """DELETE_DECK_06 — Удаление публичной колоды"""
    async def test_delete_public_deck(self, decks_service: DecksService, new_user, create_deck):
        deck = create_deck(new_user.id)
        created = await decks_service.create_deck(
            actor_id=new_user.id,
            name=deck.name,
            desc=deck.description,
            is_public=True
        )

        deleted = await decks_service.delete_deck(actor_id=new_user.id, deck_id=created.id_)
        assert deleted.id_ == created.id_
        deck_from_db = await decks_service.deck_repository.get_by_id(created.id_)
        assert deck_from_db is not None
        assert deck_from_db.deleted_at is not None