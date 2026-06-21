import re
from typing import override

from api.v1.configs.quiz_config import quiz_config
from api.v1.models import Card
from api.v1.models.types.additional_fields import AdditionalFieldType
from api.v1.services.builders.base import IPresentationBuilder
from api.v1.services.exceptions.base_exceptions import BusinessLogicException
from api.v1.services.exceptions.error_codes.quiz_error_codes import QuizErrorCodes
from api.v1.services.schemas.presentation import PresentationContext, PresentationType
from api.v1.services.utils.cards import extract_additional_field


class DefinitionPresentationBuilder(IPresentationBuilder):
    TYPE = PresentationType.DEFINITION

    @override
    async def is_available(self, card: Card) -> bool:
        return True

    @override
    async def build(self, card: Card) -> PresentationContext:
        return PresentationContext(type=self.TYPE, content=card.definition)


class ImagePresentationBuilder(IPresentationBuilder):
    TYPE = PresentationType.IMAGE

    @override
    async def is_available(self, card: Card) -> bool:
        return extract_additional_field(card, AdditionalFieldType.IMAGE) is not None

    @override
    async def build(self, card: Card) -> PresentationContext:
        image_field = extract_additional_field(card, AdditionalFieldType.IMAGE)
        if not image_field:
            raise BusinessLogicException(
                QuizErrorCodes.IMAGE_DOES_NOT_EXIST_FOR_CARD.value,
                "image_field field does not set up",
            )
        return PresentationContext(type=self.TYPE, content=image_field)


class SoundPresentationBuilder(IPresentationBuilder):
    TYPE = PresentationType.SOUND

    @override
    async def build(self, card: Card) -> PresentationContext:
        sound_field = extract_additional_field(card, AdditionalFieldType.SOUND)

        if not sound_field:
            raise BusinessLogicException(
                QuizErrorCodes.SOUND_DOES_NOT_EXIST_FOR_CARD.value,
                "sound field does not set up",
            )
        return PresentationContext(type=self.TYPE, content=sound_field)

    @override
    async def is_available(self, card: Card) -> bool:
        return extract_additional_field(card, AdditionalFieldType.SOUND) is not None


class ClozePresentationBuilder(IPresentationBuilder):
    TYPE = PresentationType.CLOZE

    @override
    async def is_available(self, card: Card) -> bool:
        return extract_additional_field(card, AdditionalFieldType.CONTEXT) is not None

    @override
    async def build(self, card: Card) -> PresentationContext:
        context_field = extract_additional_field(card, AdditionalFieldType.CONTEXT)

        if not context_field:
            raise BusinessLogicException(
                QuizErrorCodes.SOUND_DOES_NOT_EXIST_FOR_CARD.value,
                "context field does not set up",
            )
        processed_context = re.sub(quiz_config.CLOZE_EXPRESSION, quiz_config.CLOZE_SYNTAX, context_field)
        return PresentationContext(type=self.TYPE, content=processed_context)
