from dataclasses import dataclass
from enum import Enum

class AdditionalFieldType(Enum):
    IMAGE = "IMAGE"
    SOUND = "SOUND"
    CONTEXT = "CONTEXT"
    # SYNONYMS = "SYNONYMS" # TODO:  Реализовать

@dataclass
class AdditionalField:
    type: AdditionalFieldType
    content: str
