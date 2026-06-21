from abc import abstractmethod, ABC
from enum import StrEnum


class InputType(StrEnum):
    TYPING = 'typing'
    MULTIPLE_CHOICE = 'multiple_choice'
    FLASH_CARD = 'flash_card'
    TRUE_FALSE = 'true_false'


class InputContent(ABC):
    TYPE: InputType

    @abstractmethod
    def to_dict(self) -> dict:
        pass


class InputMultipleChoiceContent(InputContent):
    TYPE = InputType.MULTIPLE_CHOICE

    def __init__(self, values: list):
        self.values = values

    def to_dict(self) -> dict:
        return {"choices": self.values}


class InputTrueFalseContent(InputContent):
    TYPE = InputType.TRUE_FALSE

    def __init__(self, statement: str, is_true: bool):
        self.statement = statement
        self.is_true = is_true

    def to_dict(self) -> dict:
        return {
            "statement": self.statement,
            "is_true": self.is_true,
        }


class InputTypingContent(InputContent):
    TYPE = InputType.TYPING

    def to_dict(self) -> dict:
        return dict({})


class InputFlashCardContent(InputContent):
    TYPE = InputType.FLASH_CARD

    def to_dict(self) -> dict:
        return dict({})
