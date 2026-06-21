from dataclasses import dataclass

from .input import InputContext
from .presentation import PresentationContext


@dataclass
class Question:
    presentation: PresentationContext
    input: InputContext
