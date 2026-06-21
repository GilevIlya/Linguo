from dataclasses import dataclass
from enum import StrEnum

from api.v1.services.exceptions.base_exceptions import (
    ValidationException,
)
from api.v1.services.exceptions.error_codes.quiz_error_codes import QuizErrorCodes


class InputTypeDTO(StrEnum):
    """
        A separate layer for services in order to remove
        the dependency of the presentation layer and the domain layer
    """
    TYPING = "typing"
    MULTIPLE_CHOICE = "multiple_choice"
    FLASH_CARD = "flash_card"
    TRUE_FALSE = "true_false"


class PresentationTypeDTO(StrEnum):
    CLOZE = "cloze"
    IMAGE = "image"
    SOUND = "sound"
    DEFINITION = "definition"

@dataclass
class QuizExceptionFields:
    excepted_inputs: list[InputTypeDTO]
    excepted_presentations: list[PresentationTypeDTO]

    def __init__(self, excepted_inputs: list[str], excepted_presentations: list[str]):
        try:
            self.excepted_inputs = [InputTypeDTO(input) for input in excepted_inputs]
            self.excepted_presentations = [PresentationTypeDTO(presentation) for presentation in excepted_presentations]
        except ValueError:
            raise ValidationException(
                QuizErrorCodes.INVALID_FIELD_TYPE.value,
                message="Invalid input or presentation type"
            )