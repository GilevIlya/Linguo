from dataclasses import dataclass
from enum import StrEnum


class PresentationType(StrEnum):
    DEFINITION = 'definition'
    IMAGE = 'image'
    SOUND = 'sound'
    CLOZE = 'cloze'


@dataclass
class PresentationContext:
    type: PresentationType
    content: str
