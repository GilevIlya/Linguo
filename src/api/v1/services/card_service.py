import re
from logging import getLogger
from typing import override, Any
from uuid import UUID

from api.v1.configs.quiz_config import quiz_config
from api.v1.models import Card
from api.v1.models.types.additional_fields import AdditionalField, AdditionalFieldType
from api.v1.repositories.interfaces.ICardRepository import ICardRepository
from api.v1.repositories.interfaces.ICardReviewsRepository import ICardReviewsRepository
from api.v1.repositories.interfaces.IDeckRepository import IDeckRepository
from api.v1.schemas.responses.cards import CardSimpleView, CardDetailedView, AdditionalFieldView, \
    CardDetailedViewWithStats, CardSimpleViewWithStats
from api.v1.services.exceptions.base_exceptions import NotFoundException, BusinessLogicException, \
    PermissionDeniedException
from api.v1.services.exceptions.error_codes.base import BaseErrorCodes
from api.v1.services.exceptions.error_codes.card_error_codes import CardErrorCodes
from api.v1.services.exceptions.error_codes.decks_error_codes import DeckErrorCodes
from api.v1.services.file_service import FileService
from api.v1.services.interfaces.ICardReviewsService import ICardReviewsService
from api.v1.services.interfaces.ICardService import ICardService
from api.v1.services.interfaces.IDeckService import IDeckService
from api.v1.services.interfaces.ISrsService import ISrsService
from api.v1.services.schemas.file_param import FileParam
from api.v1.services.schemas.file_prefix import FilePrefix
from api.v1.services.user_service import UserService

logger = getLogger("app")


class CardService(ICardService):
    def __init__(
            self,
            user_service: UserService,
            deck_service: IDeckService,
            file_service: FileService,
            card_repository: ICardRepository,
            deck_repository: IDeckRepository,
            card_reviews_service: ICardReviewsService,
            card_reviews_repository: ICardReviewsRepository,
            srs_service: ISrsService,
    ):
        self.deck_repository = deck_repository
        self.card_repository = card_repository
        self.user_service = user_service
        self.deck_service = deck_service
        self.file_service = file_service
        self.card_reviews_service = card_reviews_service
        self.card_reviews_repository = card_reviews_repository
        self.srs_service = srs_service

    @override
    async def create_card(self, actor_id: UUID, term: str, def_: str, deck_id: UUID, sound: FileParam | None = None,
                          image: FileParam | None = None, context: str | None = None,
                          synonyms: tuple[str, ...] | None = None) -> CardSimpleView:
        """
        Creates a new card in the specified owner_id.

        Args:
            actor_id (UUID): ID of the user creating the card.
            term (str): The term for the card.
            def_ (str): The definition of the term.
            deck_id (UUID): ID of the owner_id to add the card to.
            sound (FileParam | None, optional): Optional sound file for the card.
            image (FileParam | None, optional): Optional image file for the card.
            context (str | None, optional): Optional context for the term.
            synonyms (tuple[str, ...] | None, optional): Optional synonyms for the term.

        Returns:
            CardSimpleView: A simplified view of the created card.
        """
        deck = await self.deck_repository.get_by_id(deck_id)
        if not deck:
            logger.warning("Deck with ID %s not found for card creation", deck_id)
            raise NotFoundException(
                error_code=DeckErrorCodes.DECK_NOT_FOUND.value,
                message="Deck with this ID not found"
            )

        if deck.user_id != actor_id:
            logger.warning("User %s does not have permission to add cards to deck %s owned by user %s", actor_id, deck_id, deck.user_id)
            raise PermissionDeniedException(
                error_code=BaseErrorCodes.PERMISSION_DENIED.value,
                message="You do not have permission to add cards to this deck"
            )

        self._validate_card_term(term)
        self._validate_card_def_(def_)

        additional_fields: list[AdditionalField] = list()

        if context is not None:
            self._validate_card_context(context)
            context_field = AdditionalField(type=AdditionalFieldType.CONTEXT, content=context)
            additional_fields.append(context_field)

        if sound is not None:
            if not sound.is_audio:
                logger.warning("Invalid sound file type: %s", sound.content_type)
                raise BusinessLogicException(
                    error_code=CardErrorCodes.INVALID_FILE_TYPE.value,
                    message="Sound file must be an audio file"
                )
            file_key = await self.file_service.upload_file(FilePrefix.CARDS_SOUNDS, sound, owner_id=actor_id)
            sound_field = AdditionalField(type=AdditionalFieldType.SOUND, content=file_key)
            additional_fields.append(sound_field)

        if image is not None:
            if not image.is_image:
                logger.warning("Invalid image file type: %s", image.content_type)
                raise BusinessLogicException(
                    error_code=CardErrorCodes.INVALID_FILE_TYPE.value,
                    message="Image file must be an image file"
                )
            file_key = await self.file_service.upload_file(FilePrefix.CARDS_IMAGES, image, owner_id=actor_id, is_public=deck.is_public)
            image_field = AdditionalField(type=AdditionalFieldType.IMAGE, content=file_key)
            additional_fields.append(image_field)

        card = Card(
            term=term,
            definition=def_,
            deck_id=deck_id,
            additional_fields=additional_fields
        )

        card = await self.card_repository.create(card)
        await self.card_reviews_service.create_card_review(actor_id=actor_id, card_id=card.id)

        return CardSimpleView(
            id_=card.id,
            term=card.term,
            def_=card.definition,
            deck_id=card.deck_id
        )

    @override
    async def delete_card(self, actor_id: UUID, id_: UUID) -> CardSimpleView:
        """
        Deletes a card if it is owned by the specified user.

        Args:
            actor_id (UUID): ID of the user attempting to delete the card.
            id_ (UUID): ID of the card to delete.

        Returns:
            CardSimpleView: A simplified view of the deleted card.
        """
        card = await self.card_repository.delete_if_owned_by(id_, actor_id)
        if card is None:
            logger.warning("Card with ID %s not found for deletion by user %s", id_, actor_id)
            raise NotFoundException(
                error_code=CardErrorCodes.CARD_NOT_FOUND.value,
                message="Card with this ID not found"
            )

        return CardSimpleView(
            id_=card.id,
            term=card.term,
            def_=card.definition,
            deck_id=card.deck_id
        )

    @override
    async def update_card(self, actor_id: UUID, card_id: UUID, term: str | None = None, def_: str | None = None,
                          sound: FileParam | None = None, image: FileParam | None = None, context: str | None = None,
                          synonyms: tuple[str, ...] | None = None) -> CardDetailedView:
        """
        Updates the details of an existing card.

        Args:
            actor_id (UUID): ID of the user attempting to update the card.
            card_id (UUID): ID of the card to update.
            term (str | None, optional): New term for the card.
            def_ (str | None, optional): New definition for the card.
            sound (FileParam | None, optional): New sound file for the card.
            image (FileParam | None, optional): New image file for the card.
            context (str | None, optional): New context for the term.
            synonyms (tuple[str, ...] | None, optional): New synonyms for the term.

        Returns:
            CardDetailedView: A detailed view of the updated card.
        """
        card = await self.card_repository.get_owned_by_user(card_id, actor_id)
        if card is None:
            logger.warning("Card with ID %s not found for update by user %s", card_id, actor_id)
            raise NotFoundException(
                error_code=CardErrorCodes.CARD_NOT_FOUND.value,
                message="Card with this ID not found"
            )

        update_data: dict[str, Any] = {}

        if term is not None:
            self._validate_card_term(term)
            update_data["term"] = term
        if def_ is not None:
            self._validate_card_def_(def_)
            update_data["definition"] = def_

        if any(f is not None for f in (image, sound, context)):
            fields = list(card.additional_fields)

            if image is not None:
                image_url = await self.file_service.upload_file(FilePrefix.CARDS_IMAGES, image, owner_id=actor_id)
                fields = [f for f in fields if f.type != AdditionalFieldType.IMAGE]
                fields.append(AdditionalField(type=AdditionalFieldType.IMAGE, content=image_url))

            if sound is not None:
                sound_url = await self.file_service.upload_file(FilePrefix.CARDS_SOUNDS, sound, owner_id=actor_id)
                fields = [f for f in fields if f.type != AdditionalFieldType.SOUND]
                fields.append(AdditionalField(type=AdditionalFieldType.SOUND, content=sound_url))

            if context is not None:
                fields = [f for f in fields if f.type != AdditionalFieldType.CONTEXT]
                if context:
                    self._validate_card_context(context)
                    fields.append(AdditionalField(type=AdditionalFieldType.CONTEXT, content=context))

            update_data["additional_fields"] = fields
        card = await self.card_repository.update(card, update_data)
        if card is None:
            logger.warning("Failed to update card with ID %s for user %s", card_id, actor_id)
            raise NotFoundException(
                error_code=CardErrorCodes.CARD_NOT_FOUND.value,
                message="Card with this ID not found"
            )

        return CardDetailedView(
            id_=card.id,
            term=card.term,
            def_=card.definition,
            deck_id=card.deck_id,
            additional_fields=tuple(
                AdditionalFieldView(type_=field.type.value, content=field.content)
                for field in card.additional_fields
            ),
            updated_at=card.updated_at,
            created_at=card.created_at
        )

    @override
    async def change_card_deck(self, actor_id: UUID, card_id: UUID, new_deck_id: UUID) -> CardSimpleView:
        """
        Changes the deck of a card if it is owned by the specified user.

        Args:
            actor_id (UUID): ID of the user attempting to change the card's deck.
            card_id (UUID): ID of the card to move.
            new_deck_id (UUID): ID of the new deck.

        Returns:
            CardSimpleView: A simplified view of the card with the updated deck.
        """
        card = await self.card_repository.get_owned_by_user(card_id, actor_id)
        if card is None:
            logger.warning("Card with ID %s not found for deck change by user %s", card_id, actor_id)
            raise NotFoundException(
                error_code=CardErrorCodes.CARD_NOT_FOUND.value,
                message="Card with this ID not found"
            )

        deck = await self.deck_repository.get_by_id(new_deck_id)
        if not deck or deck.user_id != actor_id:
            logger.warning("Deck with ID %s not found for card deck change by user %s", new_deck_id, actor_id)
            raise NotFoundException(
                error_code=DeckErrorCodes.DECK_NOT_FOUND.value,
                message="Deck with this ID not found"
            )

        card = await self.card_repository.update(card, {"deck_id": new_deck_id})
        if card is None:
            logger.warning("Failed to change deck for card with ID %s for user %s", card_id, actor_id)
            raise NotFoundException(
                error_code=CardErrorCodes.CARD_NOT_FOUND.value,
                message="Card with this ID not found"
            )

        return CardSimpleView(
            id_=card.id,
            term=card.term,
            def_=card.definition,
            deck_id=card.deck_id
        )

    @override
    async def get_card_details(self, actor_id: UUID, card_id: UUID) -> CardDetailedViewWithStats:
        """
        Retrieves detailed information about a card.

        Args:
            actor_id (UUID): ID of the user attempting to retrieve the card details.
            card_id (UUID): ID of the card to retrieve.

        Returns:
            CardDetailedViewWithStats: A detailed view of the card with statistic.
        """
        card = await self.card_repository.get_owned_by_user(card_id, actor_id)
        if card is None:
            logger.warning("Card with ID %s not found for details retrieval by user %s", card_id, actor_id)
            raise NotFoundException(
                error_code=CardErrorCodes.CARD_NOT_FOUND.value,
                message="Card with this ID not found"
            )

        additional_fields = tuple(
            AdditionalFieldView(type_=field.type.value, content=field.content)
            for field in card.additional_fields
        )
        card_review = await self.card_reviews_repository.get_by_card_id(card_id)
        if card_review is None:
            logger.warning("Card review for card with ID %s not found for details retrieval by user %s", card_id, actor_id)
            raise NotFoundException(
                error_code=CardErrorCodes.CARD_NOT_FOUND.value,
                message="Review for this card not found"
            )
        card_retrievability = self.srs_service.get_card_retrievability(card_review)

        return CardDetailedViewWithStats(
            id_=card.id,
            term=card.term,
            def_=card.definition,
            deck_id=card.deck_id,
            next_review=card_review.due,
            last_review=card_review.last_review,
            retrievability=card_retrievability,
            additional_fields=additional_fields,
            updated_at=card.updated_at,
            created_at=card.created_at
        )

    @override
    async def get_cards_by_deck(
            self,
            actor_id: UUID,
            deck_id: UUID,
            limit: int,
            offset: int,
            filter: str | None = None,
    ) -> tuple[CardSimpleViewWithStats, ...]:
        """Retrieves a list of cards in a specific deck."""
        if filter is not None and not filter.strip():
            logger.warning("Invalid filter parameter: filter is empty or whitespace for user %s", actor_id)
            raise BusinessLogicException(
                error_code=BaseErrorCodes.INVALID_FILTER.value,
                message="Filter must not be empty or whitespace"
            )

        if limit < 0 or offset < 0:
            logger.warning("Invalid pagination parameters: limit=%s, offset=%s", limit, offset)
            raise BusinessLogicException( # TODO вынести эту залупу в utils и юзать везде, где нужно
                error_code=BaseErrorCodes.INVALID_PAGINATION.value,
                message="Limit must be non-negative and offset must be non-negative"
            )
        deck = await self.deck_repository.get_by_id(deck_id)
        if not deck or deck.deleted_at is not None or (not deck.is_public and deck.user_id != actor_id):
            logger.warning("Deck with ID %s not found for cards retrieval by user %s", deck_id, actor_id)
            raise NotFoundException(
                error_code=DeckErrorCodes.DECK_NOT_FOUND.value,
                message="Deck with this ID not found"
            )
        filter = filter.strip() if filter else None
        cards = await self.card_repository.find_by_deck_id_with_stats(deck_id, limit, offset, filter)
        return tuple(
            CardSimpleViewWithStats(
                id_=card.id_,
                term=card.term,
                def_=card.def_,
                deck_id=card.deck_id,
                next_review=card.next_review,
                last_review=card.last_review,
                created_at=card.created_at
            )
            for card in cards
        )

    @override
    async def count_cards_in_deck(
            self,
            actor_id: UUID,
            deck_id: UUID,
            filter: str | None = None,
    ) -> int: # TODO добавить тесты
        if filter is not None and not filter.strip():
            logger.warning("Invalid filter parameter: filter is empty or whitespace for user %s", actor_id)
            raise BusinessLogicException(
                error_code=BaseErrorCodes.INVALID_FILTER.value,
                message="Filter must not be empty or whitespace"
            )

        deck = await self.deck_repository.get_by_id(deck_id)
        if not deck:
            logger.warning("Deck with ID %s not found for card count by user %s", deck_id, actor_id)
            raise NotFoundException(
                error_code=DeckErrorCodes.DECK_NOT_FOUND.value,
                message="Deck with this ID not found"
            )
        if not deck.is_public and deck.user_id != actor_id:
            logger.warning("Attempt to get the deck size to user without permissions", deck_id, actor_id)
            raise PermissionDeniedException(
                error_code=BaseErrorCodes.PERMISSION_DENIED.value,
                message="You do not have permission to view cards in this deck"
            )
        filter = filter.strip() if filter else None
        return await self.card_repository.count_by_deck(deck_id, filter)


    @staticmethod
    def _validate_card_term(term: str) -> None:
        """
        Validates the term of a card.

        Args:
            term (str): The term to validate.

        Raises:
            BusinessLogicException: If the term is empty or invalid.
        """
        if not term.strip():
            logger.warning("Attempt to create/update card with empty term")
            raise BusinessLogicException(CardErrorCodes.INVALID_FIELD.value, "Term must not be empty")

    @staticmethod
    def _validate_card_context(context: str) -> None:
        """
        Validates the context of a card.

        Args:
            context (str): The context to validate.

        Raises:
            BusinessLogicException: If the context is empty or invalid.
        """
        if not context.strip():
            logger.warning("Attempt to create/update card with empty context")
            raise BusinessLogicException(CardErrorCodes.INVALID_FIELD.value, "Context must not be empty")

        if len(context) > 1000:
            logger.warning("Attempt to create/update card with too long context: length=%s", len(context))
            raise BusinessLogicException(CardErrorCodes.INVALID_FIELD.value, "Context must not exceed 1000 characters")

        if not re.search(quiz_config.CLOZE_EXPRESSION, context):
            logger.warning("Attempt to create/update card with invalid context: no cloze expression found")
            raise BusinessLogicException(CardErrorCodes.INVALID_FIELD.value, "Context must contain at least one cloze expression")

    @staticmethod
    def _validate_card_def_(def_: str) -> None:
        """
        Validates the definition of a card.

        Args:
            def_ (str): The definition to validate.

        Raises:
            BusinessLogicException: If the definition is empty or invalid.
        """
        if not def_.strip():
            logger.warning("Attempt to create/update card with empty definition")
            raise BusinessLogicException(CardErrorCodes.INVALID_FIELD.value, "Definition must not be empty")