from typing import Literal
from uuid import UUID

from pydantic import BaseModel

from api.v1.services.schemas.quizzes import InputTypeDTO as InputType, PresentationTypeDTO as PresentationType


class InputMultipleChoiceContent(BaseModel):
    type: Literal[InputType.MULTIPLE_CHOICE] = InputType.MULTIPLE_CHOICE
    content: dict


# class InputTrueFalseContent(BaseModel):


class InputTypingContent(BaseModel):
    type: Literal[InputType.TYPING] = InputType.TYPING
    content: dict

class InputFlashCardContent(BaseModel):
    type: Literal[InputType.FLASH_CARD] = InputType.FLASH_CARD
    content: dict

class InputContent(BaseModel):
    type: InputType
    content: dict

# InputContent = Annotated[
#     Union[
#         InputMultipleChoiceContent,
#         # InputTrueFalseContent,
#         InputTypingContent,
#         InputFlashCardContent,
#     ],
#     Field(discriminator="type"),
# ]


class InputContext(BaseModel):
    correct_answer: str
    content: InputContent



class PresentationContext(BaseModel):
    type: PresentationType
    content: str


class Question(BaseModel):
    presentation: PresentationContext
    input: InputContext


class NextQuestion(BaseModel):
    review_id: UUID
    question: Question
