import uuid
from io import BytesIO
from unittest.mock import AsyncMock

import pytest

from api.v1.models import User, Deck
from api.v1.services.card_service import CardService
from api.v1.services.exceptions.base_exceptions import (
    NotFoundException,
    BusinessLogicException,
    PermissionDeniedException,
)
from api.v1.services.exceptions.error_codes.base import BaseErrorCodes
from api.v1.services.exceptions.error_codes.card_error_codes import CardErrorCodes
from api.v1.services.exceptions.error_codes.decks_error_codes import DeckErrorCodes
from api.v1.services.schemas.file_param import FileParam


class TestCreateCardIntegration:
    """Integration tests for create_card: service → repository → real DB."""

    # ── Happy-path ────────────────────────────────────────────────────────

    async def test_create_card_happy_path(
        self, card_service: CardService, make_user, make_deck
    ):
        """Card created with minimal fields is persisted and returned correctly."""
        # Arrange
        user: User = await make_user()
        deck: Deck = await make_deck(user_id=user.id)

        # Act
        result = await card_service.create_card(
            actor_id=user.id,
            term="apple",
            def_="яблоко",
            deck_id=deck.id,
        )

        # Assert
        assert result.term == "apple"
        assert result.def_ == "яблоко"
        assert result.deck_id == deck.id
        assert result.id_ is not None

    async def test_create_card_with_context(
        self, card_service: CardService, make_user, make_deck
    ):
        """Context additional field is persisted together with the card."""
        user = await make_user()
        deck = await make_deck(user_id=user.id)

        result = await card_service.create_card(
            actor_id=user.id,
            term="run",
            def_="бежать",
            deck_id=deck.id,
            context="She {{runs}} fast.",
        )

        # Verify via get_card_details
        details = await card_service.get_card_details(actor_id=user.id, card_id=result.id_)
        context_fields = [f for f in details.additional_fields if f.type_ == "CONTEXT"]
        assert len(context_fields) == 1
        assert context_fields[0].content == "She {{runs}} fast."

    async def test_create_card_with_sound_uploads_to_s3(
        self, card_service: CardService, make_user, make_deck, file_service_mock: AsyncMock
    ):
        user = await make_user()
        deck = await make_deck(user_id=user.id)
        file_service_mock.upload_file.return_value = "sound/some-key"

        sound = FileParam(content=BytesIO(b"audio-bytes"), content_type="audio/mpeg")
        result = await card_service.create_card(
            actor_id=user.id, term="hello", def_="привет",
            deck_id=deck.id, sound=sound,
        )

        file_service_mock.upload_file.assert_awaited_once()
        details = await card_service.get_card_details(actor_id=user.id, card_id=result.id_)
        sound_fields = [f for f in details.additional_fields if f.type_ == "SOUND"]
        assert len(sound_fields) == 1
        assert sound_fields[0].content == "sound/some-key"

    async def test_create_card_with_image_uploads_to_s3(
        self, card_service: CardService, make_user, make_deck, file_service_mock: AsyncMock
    ):
        user = await make_user()
        deck = await make_deck(user_id=user.id)
        file_service_mock.upload_file.return_value = "image/some-key"

        image = FileParam(content=BytesIO(b"image-bytes"), content_type="image/png")
        result = await card_service.create_card(
            actor_id=user.id, term="cat", def_="кот",
            deck_id=deck.id, image=image,
        )

        file_service_mock.upload_file.assert_awaited_once()
        details = await card_service.get_card_details(actor_id=user.id, card_id=result.id_)
        image_fields = [f for f in details.additional_fields if f.type_ == "IMAGE"]
        assert len(image_fields) == 1
        assert image_fields[0].content == "image/some-key"

    # ── Negative scenarios ────────────────────────────────────────────────

    async def test_create_card_deck_not_found(self, card_service: CardService, make_user):
        """Attempting to create a card in a non-existent deck raises NotFoundException."""
        user = await make_user()

        with pytest.raises(NotFoundException) as exc_info:
            await card_service.create_card(
                actor_id=user.id,
                term="apple",
                def_="яблоко",
                deck_id=uuid.uuid4(),
            )

        assert exc_info.value.error_code == DeckErrorCodes.DECK_NOT_FOUND.value

    async def test_create_card_deck_belongs_to_another_user(
        self, card_service: CardService, make_user, make_deck
    ):
        """Creating a card in someone else's deck raises PermissionDeniedException."""
        owner = await make_user(email="owner@test.com")
        other = await make_user(email="other@test.com")
        deck = await make_deck(user_id=owner.id)

        with pytest.raises(PermissionDeniedException) as exc_info:
            await card_service.create_card(
                actor_id=other.id,
                term="apple",
                def_="яблоко",
                deck_id=deck.id,
            )

        assert exc_info.value.error_code == BaseErrorCodes.PERMISSION_DENIED.value

    @pytest.mark.parametrize("term,def_", [
        ("   ", "яблоко"),
        ("", "яблоко"),
    ])
    async def test_create_card_empty_term_raises_validation_error(
        self, card_service: CardService, make_user, make_deck, term, def_
    ):
        """Empty or whitespace-only term raises BusinessLogicException."""
        user = await make_user()
        deck = await make_deck(user_id=user.id)

        with pytest.raises(BusinessLogicException) as exc_info:
            await card_service.create_card(
                actor_id=user.id, term=term, def_=def_, deck_id=deck.id
            )

        assert exc_info.value.error_code == CardErrorCodes.INVALID_FIELD.value

    @pytest.mark.parametrize("term,def_", [
        ("apple", "   "),
        ("apple", ""),
    ])
    async def test_create_card_empty_definition_raises_validation_error(
        self, card_service: CardService, make_user, make_deck, term, def_
    ):
        """Empty or whitespace-only definition raises BusinessLogicException."""
        user = await make_user()
        deck = await make_deck(user_id=user.id)

        with pytest.raises(BusinessLogicException) as exc_info:
            await card_service.create_card(
                actor_id=user.id, term=term, def_=def_, deck_id=deck.id
            )

        assert exc_info.value.error_code == CardErrorCodes.INVALID_FIELD.value

    async def test_create_card_invalid_sound_type_raises_error(
        self, card_service: CardService, make_user, make_deck
    ):
        """Non-audio file passed as sound raises BusinessLogicException."""
        user = await make_user()
        deck = await make_deck(user_id=user.id)

        # Manually override is_audio to simulate wrong type check at service level
        # FileParam validates content_type in __post_init__, so we test with valid audio prefix
        # but the service also checks is_audio. Let's test with image passed as sound.
        image_as_sound = FileParam(content=BytesIO(b"data"), content_type="image/png")

        with pytest.raises(BusinessLogicException) as exc_info:
            await card_service.create_card(
                actor_id=user.id, term="test", def_="тест",
                deck_id=deck.id, sound=image_as_sound,
            )

        assert exc_info.value.error_code == CardErrorCodes.INVALID_FILE_TYPE.value

    async def test_create_card_invalid_image_type_raises_error(
        self, card_service: CardService, make_user, make_deck
    ):
        """Non-image file passed as image raises BusinessLogicException."""
        user = await make_user()
        deck = await make_deck(user_id=user.id)

        audio_as_image = FileParam(content=BytesIO(b"data"), content_type="audio/mpeg")

        with pytest.raises(BusinessLogicException) as exc_info:
            await card_service.create_card(
                actor_id=user.id, term="test", def_="тест",
                deck_id=deck.id, image=audio_as_image,
            )

        assert exc_info.value.error_code == CardErrorCodes.INVALID_FILE_TYPE.value

