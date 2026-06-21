import uuid
from io import BytesIO
from unittest.mock import AsyncMock, MagicMock

import pytest

from api.v1.models.types.additional_fields import AdditionalFieldType
from api.v1.services.exceptions.base_exceptions import (
    BusinessLogicException,
    NotFoundException,
    PermissionDeniedException,
)
from api.v1.services.exceptions.error_codes.card_error_codes import CardErrorCodes
from api.v1.services.exceptions.error_codes.decks_error_codes import DeckErrorCodes
from api.v1.services.schemas.file_param import FileParam
from tests.card_service.helpers import _make_card, _make_deck


class TestCreateCard:
    # CREATE_CARD_01
    async def test_create_card_returns_simple_view_with_correct_fields(
        self, card_svc, card_repository: AsyncMock, deck_repository: AsyncMock
    ):
        user_id = uuid.uuid4()
        deck_id = uuid.uuid4()
        deck = _make_deck(deck_id=deck_id, user_id=user_id)
        created_card = _make_card(term="apple", definition="яблоко", deck_id=deck_id)
        deck_repository.get_by_id.return_value = deck
        card_repository.create.return_value = created_card

        result = await card_svc.create_card(
            actor_id=user_id, term="apple", def_="яблоко", deck_id=deck_id
        )

        assert result.term == "apple"
        assert result.def_ == "яблоко"
        assert result.deck_id == deck_id
        assert result.id_ == created_card.id

        card_repository.create.assert_awaited_once()

    # CREATE_CARD_02
    async def test_create_card_with_context_saves_context_in_additional_fields(
        self, card_svc, card_repository: AsyncMock, deck_repository: AsyncMock
    ):
        user_id = uuid.uuid4()
        deck_id = uuid.uuid4()
        deck = _make_deck(deck_id=deck_id, user_id=user_id)
        deck_repository.get_by_id.return_value = deck
        card_repository.create.return_value = _make_card(deck_id=deck_id)

        await card_svc.create_card(
            actor_id=user_id, term="run", def_="бежать", deck_id=deck_id,
            context="She {{runs}} fast.",
        )

        created_entity = card_repository.create.call_args[0][0]
        context_fields = [
            f for f in created_entity.additional_fields
            if f.type == AdditionalFieldType.CONTEXT
        ]
        assert len(context_fields) == 1
        assert context_fields[0].content == "She {{runs}} fast."

    async def test_create_card_with_sound_uploads_to_s3_and_saves_field(
        self, card_svc, card_repository: AsyncMock, deck_repository: AsyncMock, file_service_svc: AsyncMock
    ):
        user_id = uuid.uuid4()
        deck_id = uuid.uuid4()
        deck = _make_deck(deck_id=deck_id, user_id=user_id)
        deck_repository.get_by_id.return_value = deck
        card_repository.create.return_value = _make_card(deck_id=deck_id)
        file_service_svc.upload_file.return_value = "sound/test-key"

        sound = FileParam(content=BytesIO(b"audio bytes"), content_type="audio/mpeg")
        await card_svc.create_card(
            actor_id=user_id, term="run", def_="бежать", deck_id=deck_id, sound=sound
        )

        file_service_svc.upload_file.assert_awaited_once()
        created_entity = card_repository.create.call_args[0][0]
        sound_fields = [f for f in created_entity.additional_fields if f.type == AdditionalFieldType.SOUND]
        assert len(sound_fields) == 1
        assert sound_fields[0].content == "sound/test-key"

    async def test_create_card_with_image_uploads_to_s3_and_saves_field(
        self, card_svc, card_repository: AsyncMock, deck_repository: AsyncMock, file_service_svc: AsyncMock
    ):
        user_id = uuid.uuid4()
        deck_id = uuid.uuid4()
        deck = _make_deck(deck_id=deck_id, user_id=user_id)
        deck_repository.get_by_id.return_value = deck
        card_repository.create.return_value = _make_card(deck_id=deck_id)
        file_service_svc.upload_file.return_value = "image/test-key"

        image = FileParam(content=BytesIO(b"image bytes"), content_type="image/png")
        await card_svc.create_card(
            actor_id=user_id, term="run", def_="бежать", deck_id=deck_id, image=image
        )

        file_service_svc.upload_file.assert_awaited_once()
        created_entity = card_repository.create.call_args[0][0]
        image_fields = [f for f in created_entity.additional_fields if f.type == AdditionalFieldType.IMAGE]
        assert len(image_fields) == 1
        assert image_fields[0].content == "image/test-key"

    # CREATE_CARD_03 / CREATE_CARD_04 / CREATE_CARD_05
    @pytest.mark.parametrize("term,def_", [
        ("", "яблоко"),     # CREATE_CARD_03: empty term
        ("apple", ""),      # CREATE_CARD_04: empty definition
        ("   ", "яблоко"),  # CREATE_CARD_05: whitespace-only term
    ])
    async def test_create_card_invalid_term_or_def_raises_business_logic_exception(
        self, card_svc, deck_repository: AsyncMock, term: str, def_: str
    ):
        user_id = uuid.uuid4()
        deck_id = uuid.uuid4()
        deck_repository.get_by_id.return_value = _make_deck(deck_id=deck_id, user_id=user_id)

        with pytest.raises(BusinessLogicException) as exc_info:
            await card_svc.create_card(
                actor_id=user_id, term=term, def_=def_, deck_id=deck_id
            )

        assert exc_info.value.error_code == CardErrorCodes.INVALID_FIELD.value

    # CREATE_CARD_06
    async def test_create_card_deck_not_found_raises_not_found_exception(
        self, card_svc, deck_repository: AsyncMock
    ):
        deck_repository.get_by_id.return_value = None

        with pytest.raises(NotFoundException) as exc_info:
            await card_svc.create_card(
                actor_id=uuid.uuid4(), term="apple", def_="яблоко", deck_id=uuid.uuid4()
            )

        assert exc_info.value.error_code == DeckErrorCodes.DECK_NOT_FOUND.value

    # CREATE_CARD_07
    async def test_create_card_deck_owned_by_another_user_raises_permission_denied(
        self, card_svc, deck_repository: AsyncMock
    ):
        user_a = uuid.uuid4()
        deck = _make_deck(user_id=uuid.uuid4())  # owned by a different user
        deck_repository.get_by_id.return_value = deck

        with pytest.raises(PermissionDeniedException):
            await card_svc.create_card(
                actor_id=user_a, term="apple", def_="яблоко", deck_id=deck.id
            )

    # CREATE_CARD_09
    async def test_create_card_non_audio_sound_raises_invalid_file_type(
        self, card_svc, deck_repository: AsyncMock
    ):
        user_id = uuid.uuid4()
        deck_id = uuid.uuid4()
        deck_repository.get_by_id.return_value = _make_deck(deck_id=deck_id, user_id=user_id)

        sound = MagicMock()
        sound.is_audio = False
        sound.content_type = "image/png"
        sound.content = BytesIO(b"data")

        with pytest.raises(BusinessLogicException) as exc_info:
            await card_svc.create_card(
                actor_id=user_id, term="apple", def_="яблоко", deck_id=deck_id, sound=sound
            )

        assert exc_info.value.error_code == CardErrorCodes.INVALID_FILE_TYPE.value

    async def test_create_card_non_image_file_raises_invalid_file_type(
        self, card_svc, deck_repository: AsyncMock
    ):
        user_id = uuid.uuid4()
        deck_id = uuid.uuid4()
        deck_repository.get_by_id.return_value = _make_deck(deck_id=deck_id, user_id=user_id)

        image = MagicMock()
        image.is_image = False
        image.content_type = "audio/mpeg"
        image.content = BytesIO(b"data")

        with pytest.raises(BusinessLogicException) as exc_info:
            await card_svc.create_card(
                actor_id=user_id, term="apple", def_="яблоко", deck_id=deck_id, image=image
            )

        assert exc_info.value.error_code == CardErrorCodes.INVALID_FILE_TYPE.value
