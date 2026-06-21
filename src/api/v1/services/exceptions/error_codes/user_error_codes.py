from enum import Enum


class UserErrorCodes(Enum):
    USER_NOT_FOUND = "USER_NOT_FOUND"
    EMAIL_ALREADY_IN_USE = "EMAIL_ALREADY_IN_USE"
