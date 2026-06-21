import uuid
from logging import getLogger
from typing import Any, List, override

from api.v1.configs.pagination import pagination_config
from api.v1.models.decks import Deck
from api.v1.repositories.interfaces.IDeckRepository import IDeckRepository
from api.v1.schemas.responses.decks import DeckDetailedView, DeckSimpleView, DeckWithStatsView
from api.v1.services.exceptions.base_exceptions import NotFoundException, ValidationException, PermissionDeniedException
from api.v1.services.exceptions.error_codes.base import BaseErrorCodes
from api.v1.services.exceptions.error_codes.decks_error_codes import DeckErrorCodes
from api.v1.services.interfaces.IDeckService import IDeckService
from api.v1.utils.pagination import Pagination

logger = getLogger("app")


class DecksService(IDeckService):
    COUNT_RECENTLY_STUDIED_DECKS: int = 3 # TODO:/ вынести в конфиш

    def __init__(self, deck_repository: IDeckRepository):
        self.deck_repository = deck_repository

    @override
    async def create_deck(
        self, 
        actor_id: uuid.UUID, 
        name: str,
        desc: str | None,
        is_public: bool = False
    ):

        self._validate_deck_name(name)
        deck = Deck(
            user_id=actor_id,
            name=name,
            description=desc or "",
            is_public=is_public
        )
        deck = await self.deck_repository.create(deck)
        return DeckSimpleView(
            id_=deck.id,
            title=deck.name,
            description=deck.description,
            is_public=deck.is_public
        )

    @override
    async def get_decks_for_user(
        self, 
        actor_id: uuid.UUID, 
        offset: int = 0,
        limit: int = 50
    ) -> List[Any]:

        self._validate_pagination(limit, offset)
        decks = await self.deck_repository.find_by_user_id(actor_id, limit, offset)
        return [
            DeckSimpleView(
                id_=deck.id,
                title=deck.name,
                description=deck.description,
                is_public=deck.is_public
            ) for deck in decks
        ]

    @override
    async def get_paginated_decks_for_user(
        self,
        actor_id: uuid.UUID,
        name: str | None = None,
        page: int = pagination_config.DEFAULT_PAGE
    ):

        if page < 1:
            raise ValidationException(
                error_code=BaseErrorCodes.INVALID_PAGINATION.value,
                message="Page must be greater than 0"
            )

        total = await self.deck_repository.count(filters={"user_id": actor_id, "deleted_at": None})
        pagination = Pagination(
            total=total,
            current_page=page,
            per_page=pagination_config.DEFAULT_PER_PAGE
        )

        resp = await self.deck_repository.find_by_user_id_with_stats(
            actor_id,
            name=name,
            limit=pagination.per_page,
            offset=pagination.start
        )

        deck_views = [
            DeckWithStatsView(
                id_=i.deck.id,
                title=i.deck.name,
                description=i.deck.description,
                is_public=i.deck.is_public,
                total_cards=i.total_cards,
                cards_to_learn=i.cards_to_learn,
            )
            for i in resp
        ]
        return deck_views, pagination

    @override
    async def update_deck(
        self,
        actor_id: uuid.UUID,
        deck_id: uuid.UUID,
        new_name: str | None = None,
        new_desc: str | None = None,
        is_public: bool | None = None,
    ):

        deck = await self._get_validated_deck_by_id(deck_id)
        self._check_owner(deck=deck, actor_id=actor_id)

        update_data: dict[str, Any] = {}

        if new_name is not None:
            self._validate_deck_name(new_name)
            update_data["name"] = new_name.strip()

        if new_desc is not None:
            update_data["description"] = new_desc.strip()

        if is_public is not None:
            update_data["is_public"] = is_public

        updated_deck = await self.deck_repository.update(deck, update_data)
        return DeckSimpleView(
            id_=updated_deck.id,
            title=updated_deck.name,
            description=updated_deck.description,
            is_public=updated_deck.is_public or False
        )

    @override   
    async def delete_deck(
        self,  
        actor_id: uuid.UUID, 
        deck_id: uuid.UUID
    ):

        deck = await self._get_validated_deck_by_id(deck_id)
        self._check_owner(actor_id=actor_id, deck=deck)
        
        deleted_deck = await self.deck_repository.soft_delete(deck)
        return DeckSimpleView(
            id_=deleted_deck.id,
            title=deleted_deck.name,
            description=deleted_deck.description,
            is_public=deleted_deck.is_public
        )

    @override
    async def get_deck_details(
        self,
        actor_id: uuid.UUID,
        deck_id: uuid.UUID,
    ):

        deck = await self._get_validated_deck_by_id(deck_id)
        if not deck.is_public and deck.user_id != actor_id:
            raise PermissionDeniedException(
                error_code=DeckErrorCodes.DECK_BELONGS_TO_ANOTHER_USER.value,
                message="Permission denied: You are not the owner of this deck")

        return DeckDetailedView(
            id_=deck.id,
            title=deck.name,
            description=deck.description,
            is_public=deck.is_public,
            created_at=deck.created_at,
            updated_at=deck.updated_at,
        )

    @override
    async def get_recently_studied_decks(
        self,
        actor_id: uuid.UUID,
    ) -> list[DeckSimpleView]:

        decks = await self.deck_repository.find_recently_studied_by_user_id(actor_id, self.COUNT_RECENTLY_STUDIED_DECKS)
        return [
            DeckSimpleView(
                id_=deck.id,
                title=deck.name,
                description=deck.description,
                is_public=deck.is_public,
            )
            for deck in decks
        ]

    @override
    async def get_paginated_active_decks_for_user(
            self,
            actor_id: uuid.UUID,
            page: int = 1
    ) -> tuple[list[DeckWithStatsView], Pagination]:

        total_decks = await self.deck_repository.count(filters={"user_id": actor_id, "deleted_at": None}) # TODO ебать пофиксить баг, неправильная пагинация. Надо еще что бы card_reviews было учитывать, а то может быть 0 карточек для изучения, но при этом карточки есть и пагинация будет работать неправильно
        paginator = Pagination(
            total=total_decks,
            current_page=page,
            per_page=pagination_config.DEFAULT_PER_PAGE
        )

        resp = await self.deck_repository.find_active_by_user_id_with_metrics(
            actor_id,
            limit=paginator.per_page,
            offset=paginator.start,
        )

        return ([
            DeckWithStatsView(
                id_=i.deck.id,
                title=i.deck.name,
                description=i.deck.description,
                is_public=i.deck.is_public,
                total_cards=i.total_cards,
                cards_to_learn=i.cards_to_learn,
            )
            for i in resp
        ], paginator)

    @staticmethod
    def _validate_pagination(limit: int, offset: int) -> None:
        if limit < 0 or offset < 0:
            raise ValidationException(
                error_code=BaseErrorCodes.INVALID_PAGINATION.value,
                message="Limit and offset must be non-negative"
            )

    async def _get_validated_deck_by_id(self, deck_id: uuid.UUID) -> Deck:
        deck = await self.deck_repository.get_by_id(deck_id, filters={"deleted_at": None})
        if not deck:
            raise NotFoundException(
                error_code=DeckErrorCodes.DECK_NOT_FOUND.value,
                message="Deck with this ID not found")
        return deck

    def _check_owner(self, deck: Deck, actor_id: uuid.UUID) -> None:
        if deck.user_id != actor_id:
            raise PermissionDeniedException(
                error_code=DeckErrorCodes.DECK_BELONGS_TO_ANOTHER_USER.value,
                message="Permission denied: you are not the owner of this deck"
        )

    @staticmethod
    def _validate_deck_name(name: str | None) -> None:
        if name is None or not name.strip():
            raise ValidationException(
                error_code=DeckErrorCodes.INVALID_DECK_NAME.value,
                message="Deck name cannot be empty or whitespace"
            )
