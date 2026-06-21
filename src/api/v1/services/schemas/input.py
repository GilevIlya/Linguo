from dataclasses import dataclass
from typing import TypeVar, Generic

from api.v1.services.schemas.input_contents import InputType, InputContent

T = TypeVar("T", bound=InputContent)

@dataclass
class InputContext(Generic[T]):
    correct_answer: str
    content: T

    @property
    def type(self) -> InputType:
        return self.content.TYPE

