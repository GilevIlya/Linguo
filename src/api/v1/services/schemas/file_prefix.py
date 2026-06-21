from enum import Enum

class FilePrefix(str, Enum):
    AVATARS = "USERS/AVATARS"
    CARDS_IMAGES = "CARDS/IMAGES"
    CARDS_SOUNDS = "CARDS/SOUNDS"