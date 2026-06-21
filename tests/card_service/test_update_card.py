import uuid
from io import BytesIO
from unittest.mock import AsyncMock

import pytest

from api.v1.models.types.additional_fields import AdditionalField, AdditionalFieldType
from api.v1.services.exceptions.base_exceptions import BusinessLogicException
from api.v1.services.exceptions.error_codes.card_error_codes import CardErrorCodes
from api.v1.services.schemas.file_param import FileParam
from tests.card_service.helpers import _make_card


class TestUpdateCard:
    # UPDATE_CARD_01
    async def test_update_card_term_only_returns_view_with_new_term(
        self, card_svc, card_repository: AsyncMock
    ):
        user_id = uuid.uuid4()
        card_id = uuid.uuid4()
        deck_id = uuid.uuid4()
        existing = _make_card(card_id=card_id, term="apple", definition="яблоко", deck_id=deck_id)
        updated = _make_card(card_id=card_id, term="pear", definition="яблоко", deck_id=deck_id)
        card_repository.get_owned_by_user.return_value = existing
        card_repository.update.return_value = updated

        result = await card_svc.update_card(actor_id=user_id, card_id=card_id, term="pear")

        assert result.term == "pear"
        assert result.def_ == "яблоко"

    async def test_update_card_term_only_does_not_pass_definition_to_repository(
        self, card_svc, card_repository: AsyncMock
    ):
        user_id = uuid.uuid4()
        card_id = uuid.uuid4()
        card_repository.get_owned_by_user.return_value = _make_card(card_id=card_id)
        card_repository.update.return_value = _make_card(card_id=card_id, term="pear")

        await card_svc.update_card(actor_id=user_id, card_id=card_id, term="pear")

        update_data = card_repository.update.call_args[0][1]
        assert update_data.get("term") == "pear"
        assert "definition" not in update_data

    # UPDATE_CARD_02
    async def test_update_card_def_only_returns_view_with_new_definition(
        self, card_svc, card_repository: AsyncMock
    ):
        user_id = uuid.uuid4()
        card_id = uuid.uuid4()
        deck_id = uuid.uuid4()
        existing = _make_card(card_id=card_id, term="apple", definition="яблоко", deck_id=deck_id)
        updated = _make_card(card_id=card_id, term="apple", definition="новое определение", deck_id=deck_id)
        card_repository.get_owned_by_user.return_value = existing
        card_repository.update.return_value = updated

        result = await card_svc.update_card(
            actor_id=user_id, card_id=card_id, def_="новое определение"
        )

        assert result.def_ == "новое определение"
        assert result.term == "apple"

    # UPDATE_CARD_03
    async def test_update_card_all_none_returns_unchanged_view(
        self, card_svc, card_repository: AsyncMock
    ):
        user_id = uuid.uuid4()
        card_id = uuid.uuid4()
        deck_id = uuid.uuid4()
        existing = _make_card(card_id=card_id, term="apple", definition="яблоко", deck_id=deck_id)
        card_repository.get_owned_by_user.return_value = existing
        card_repository.update.return_value = existing

        result = await card_svc.update_card(actor_id=user_id, card_id=card_id)

        assert result.term == "apple"
        assert result.def_ == "яблоко"

    # UPDATE_CARD_04
    @pytest.mark.parametrize("term,def_", [
        ("", None),     # empty term
        (None, ""),     # empty definition
    ])
    async def test_update_card_empty_fields_raise_business_logic_exception(
        self, card_svc, card_repository: AsyncMock, term, def_
    ):
        card_repository.get_owned_by_user.return_value = _make_card()

        with pytest.raises(BusinessLogicException) as exc_info:
            await card_svc.update_card(
                actor_id=uuid.uuid4(), card_id=uuid.uuid4(), term=term, def_=def_
            )

        assert exc_info.value.error_code == CardErrorCodes.INVALID_FIELD.value

    # UPDATE_CARD_05
    async def test_update_card_with_image_uploads_to_s3_and_replaces_old_image_field(
        self, card_svc, card_repository: AsyncMock, file_service_svc : AsyncMock
    ):
        """Передаём новое изображение: s3.save_file вызывается, старое IMAGE-поле фильтруется,
        в additional_fields появляется только одно IMAGE-поле с новым ключом."""
        user_id = uuid.uuid4()
        card_id = uuid.uuid4()
        old_image_field = AdditionalField(type=AdditionalFieldType.IMAGE, content="old-image-key")
        existing = _make_card(card_id=card_id, additional_fields=[old_image_field])
        updated = _make_card(card_id=card_id)
        card_repository.get_owned_by_user.return_value = existing
        card_repository.update.return_value = updated
        file_service_svc .upload_file.return_value = "new-image-key"

        new_image = FileParam(content=BytesIO(b"img bytes"), content_type="image/jpeg")
        await card_svc.update_card(actor_id=user_id, card_id=card_id, image=new_image)

        # s3 вызван с нужным типом и контентом
        file_service_svc.upload_file.assert_awaited_once()

        # в additional_fields передан список без старого поля и с новым
        update_data = card_repository.update.call_args[0][1]
        new_fields = update_data["additional_fields"]
        image_fields = [f for f in new_fields if f.type == AdditionalFieldType.IMAGE]
        assert len(image_fields) == 1
        assert image_fields[0].content == "new-image-key"

    # UPDATE_CARD_06
    async def test_update_card_with_sound_uploads_to_s3_and_replaces_old_sound_field(
        self, card_svc, card_repository: AsyncMock, file_service_svc : AsyncMock
    ):
        """Передаём новый звук: s3.save_file вызывается, старое SOUND-поле фильтруется,
        в additional_fields появляется только одно SOUND-поле с новым ключом."""
        user_id = uuid.uuid4()
        card_id = uuid.uuid4()
        old_sound_field = AdditionalField(type=AdditionalFieldType.SOUND, content="old-sound-key")
        existing = _make_card(card_id=card_id, additional_fields=[old_sound_field])
        updated = _make_card(card_id=card_id)
        card_repository.get_owned_by_user.return_value = existing
        card_repository.update.return_value = updated
        file_service_svc.upload_file.return_value = "new-sound-key"

        new_sound = FileParam(content=BytesIO(b"audio bytes"), content_type="audio/mpeg")
        await card_svc.update_card(actor_id=user_id, card_id=card_id, sound=new_sound)

        # s3 вызван с нужным типом и контентом
        file_service_svc.upload_file.assert_awaited_once()

        # в additional_fields передан список без старого поля и с новым
        update_data = card_repository.update.call_args[0][1]
        new_fields = update_data["additional_fields"]
        sound_fields = [f for f in new_fields if f.type == AdditionalFieldType.SOUND]
        assert len(sound_fields) == 1
        assert sound_fields[0].content == "new-sound-key"

    # UPDATE_CARD_07
    async def test_update_card_with_image_when_no_previous_image_adds_new_field(
        self, card_svc, card_repository: AsyncMock, file_service_svc : AsyncMock
    ):
        """Карточка без IMAGE-поля: после обновления в additional_fields появляется ровно одно IMAGE-поле."""
        user_id = uuid.uuid4()
        card_id = uuid.uuid4()
        # карточка без полей вообще
        existing = _make_card(card_id=card_id, additional_fields=[])
        updated = _make_card(card_id=card_id)
        card_repository.get_owned_by_user.return_value = existing
        card_repository.update.return_value = updated
        file_service_svc.upload_file.return_value = "brand-new-image-key"

        new_image = FileParam(content=BytesIO(b"img bytes"), content_type="image/png")
        await card_svc.update_card(actor_id=user_id, card_id=card_id, image=new_image)

        update_data = card_repository.update.call_args[0][1]
        new_fields = update_data["additional_fields"]
        image_fields = [f for f in new_fields if f.type == AdditionalFieldType.IMAGE]
        assert len(image_fields) == 1
        assert image_fields[0].content == "brand-new-image-key"

