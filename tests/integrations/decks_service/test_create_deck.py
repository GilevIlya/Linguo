import pytest
from api.v1.services.decks_service import DecksService
from api.v1.services.exceptions.base_exceptions import ValidationException


class TestDeckCreation:
    """CREATE_DECK_01 — Успешное создание приватной колоды (is_public=False по умолчанию)"""
    async def test_create_deck(self, decks_service: DecksService, new_user, create_deck):
        deck = create_deck(new_user.id)
        created_deck = await decks_service.create_deck(
            actor_id=new_user.id,
            name=deck.name,
            desc=deck.description
        )

        assert created_deck.title == deck.name
        assert created_deck.description == deck.description
        assert created_deck.is_public is False

    """CREATE_DECK_02 — Успешное создание публичной колоды"""
    async def test_create_public_deck(self, decks_service: DecksService, new_user, create_deck):
        deck = create_deck(new_user.id)
        created_deck = await decks_service.create_deck(
            actor_id=new_user.id,
            name=deck.name,
            desc=deck.description,
            is_public=True
        )

        assert created_deck.title == deck.name
        assert created_deck.description == deck.description
        assert created_deck.is_public is True

    """CREATE_DECK_03 — Пустое поле name → ValidationException"""
    async def test_create_deck_empty_name_raises(self, decks_service: DecksService, new_user):
        with pytest.raises(ValidationException) as exc_info:
            await decks_service.create_deck(
                actor_id=new_user.id,
                name="",
                desc="Описание"
            )
        assert exc_info.value.error_code == "INVALID_DECK_NAME"

    """CREATE_DECK_04 — name содержит только пробелы → ValidationException"""
    async def test_create_deck_whitespace_name_raises(self, decks_service: DecksService, new_user):
        with pytest.raises(ValidationException) as exc_info:
            await decks_service.create_deck(
                actor_id=new_user.id,
                name="   ",
                desc="Описание"
            )
        assert exc_info.value.error_code == "INVALID_DECK_NAME"

    """CREATE_DECK_05 — Пустое поле desc разрешено"""
    async def test_create_deck_empty_description_allowed(self, decks_service: DecksService, new_user):
        created_deck = await decks_service.create_deck(
            actor_id=new_user.id,
            name="Deck with empty desc",
            desc=""
        )

        assert created_deck.title == "Deck with empty desc"
        assert created_deck.description == ""
        assert created_deck.is_public is False

    """CREATE_DECK_06 — Колода привязывается к actor_id (тот же новый юзер)"""
    async def test_create_deck_belongs_to_correct_user(
        self, decks_service: DecksService, new_user, create_deck
    ):
        deck = create_deck(new_user.id)
        created_deck = await decks_service.create_deck(
            actor_id=new_user.id,
            name=deck.name,
            desc=deck.description
        )
        assert created_deck.title == deck.name
        assert created_deck.description == deck.description

        # Проверка привязки к пользователю через репозиторий
        deck_from_db = await decks_service.deck_repository.get_by_id(created_deck.id_)
        assert deck_from_db is not None
        assert deck_from_db.user_id == new_user.id