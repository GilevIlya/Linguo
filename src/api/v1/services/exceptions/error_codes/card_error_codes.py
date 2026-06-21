from enum import Enum


class CardErrorCodes(Enum):
    INVALID_FILE_TYPE = "INVALID_FILE_TYPE"
    INVALID_FIELD = "INVALID_FIELD"
    CARD_NOT_FOUND = "CARD_NOT_FOUND"
