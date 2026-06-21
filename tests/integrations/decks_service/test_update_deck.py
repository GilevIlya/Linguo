import pytest
import uuid

from api.v1.services.decks_service import DecksService
from api.v1.services.exceptions.base_exceptions import ValidationException, PermissionDeniedException, NotFoundException


class TestDeckUpdate:

    """UPDATE_DECK_01 — Успешное обновление только имени"""
    async def test_update_deck_name_only(self, decks_service: DecksService, new_user, create_deck):
        deck = create_deck(new_user.id)
        created = await decks_service.create_deck(
            actor_id=new_user.id,
            name=deck.name,
            desc=deck.description,
            is_public=False
        )

        updated = await decks_service.update_deck(
            actor_id=new_user.id,
            deck_id=created.id_,
            new_name="New Name"
        )

        assert updated.title == "New Name"
        assert updated.description == deck.description
        assert updated.is_public is False

    """UPDATE_DECK_02 — Успешное обновление только описания"""
    async def test_update_deck_description_only(self, decks_service: DecksService, new_user, create_deck):
        deck = create_deck(new_user.id)
        created = await decks_service.create_deck(
            actor_id=new_user.id,
            name=deck.name,
            desc=deck.description
        )

        updated = await decks_service.update_deck(
            actor_id=new_user.id,
            deck_id=created.id_,
            new_desc="New Description"
        )

        assert updated.description == "New Description"
        assert updated.title == deck.name
        assert updated.is_public is False

    """UPDATE_DECK_03 — Смена видимости"""
    async def test_update_deck_toggle_public(self, decks_service: DecksService, new_user, create_deck):
        deck = create_deck(new_user.id)
        created = await decks_service.create_deck(
            actor_id=new_user.id,
            name=deck.name,
            desc=deck.description,
            is_public=False
        )

        updated = await decks_service.update_deck(
            actor_id=new_user.id,
            deck_id=created.id_,
            is_public=True
        )

        assert updated.is_public is True
        assert updated.title == deck.name
        assert updated.description == deck.description

    """UPDATE_DECK_04 — Все поля None → колода не меняется"""
    async def test_update_deck_no_changes(self, decks_service: DecksService, new_user, create_deck):
        deck = create_deck(new_user.id)
        created = await decks_service.create_deck(
            actor_id=new_user.id,
            name=deck.name,
            desc=deck.description
        )

        updated = await decks_service.update_deck(
            actor_id=new_user.id,
            deck_id=created.id_
        )

        assert updated.title == deck.name
        assert updated.description == deck.description
        assert updated.is_public is False

    """UPDATE_DECK_05 — Обновление new_name на пустую строку → ValidationException"""
    async def test_update_deck_empty_name_raises(self, decks_service: DecksService, new_user, create_deck):
        deck = create_deck(new_user.id)
        created = await decks_service.create_deck(
            actor_id=new_user.id,
            name=deck.name,
            desc=deck.description
        )

        with pytest.raises(ValidationException) as exc_info:
            await decks_service.update_deck(
                actor_id=new_user.id,
                deck_id=created.id_,
                new_name=""
            )
        assert exc_info.value.error_code == "INVALID_DECK_NAME"

    """UPDATE_DECK_06 — Колода не найдена"""
    async def test_update_nonexistent_deck_raises(self, decks_service: DecksService, new_user):
        non_existent_id = uuid.uuid4()
        with pytest.raises(NotFoundException):
            await decks_service.update_deck(
                actor_id=new_user.id,
                deck_id=non_existent_id,
                new_name="New"
            )

    """UPDATE_DECK_07 — Колода принадлежит другому пользователю"""
    async def test_update_deck_permission_denied(self, decks_service: DecksService, new_user, create_user, session, create_deck):
        # Создаём второго пользователя и его колоду
        user_b = create_user()
        from api.v1.services.user_service import UserService
        from api.v1.repositories.user_repository import UserRepository

        user_service = UserService(UserRepository(session))
        persisted_user_b = await user_service.create_user(user_b)

        deck_b = create_deck(persisted_user_b.id)
        created_b = await decks_service.create_deck(
            actor_id=persisted_user_b.id,
            name=deck_b.name,
            desc=deck_b.description
        )

        with pytest.raises(PermissionDeniedException):
            await decks_service.update_deck(
                actor_id=new_user.id,
                deck_id=created_b.id_,
                new_name="Hacked"
            )

    """UPDATE_DECK_08 — Обновление мягко удалённой колоды"""
    async def test_update_soft_deleted_deck(self, decks_service: DecksService, new_user, create_deck):
        deck = create_deck(new_user.id)
        created = await decks_service.create_deck(
            actor_id=new_user.id,
            name=deck.name,
            desc=deck.description
        )
        created_deck_from_db = await decks_service.deck_repository.get_by_id(created.id_)

        if created_deck_from_db:
            deleted_deck = await decks_service.deck_repository.soft_delete(created_deck_from_db)

            assert deleted_deck.deleted_at is not None

            with pytest.raises(NotFoundException):
                await decks_service.update_deck(
                    actor_id=new_user.id,
                    deck_id=created.id_,
                    new_name="New Name"
                )