from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from api.v1.services.exceptions.error_codes.auth_error_codes import AuthErrorCodes
from api.v1.services.exceptions.error_codes.base import BaseErrorCodes
from api.v1.services.exceptions.error_codes.card_error_codes import CardErrorCodes
from api.v1.services.exceptions.error_codes.decks_error_codes import DeckErrorCodes
from api.v1.services.exceptions.error_codes.files_error_codes import FilesErrorCodes
from api.v1.services.exceptions.error_codes.profiles_error_codes import ProfilesErrorCodes
from api.v1.services.exceptions.error_codes.quiz_error_codes import QuizErrorCodes
from api.v1.services.exceptions.error_codes.user_error_codes import UserErrorCodes

Error_codes = [
    BaseErrorCodes,
    QuizErrorCodes,
    AuthErrorCodes,
    CardErrorCodes,
    DeckErrorCodes,
    FilesErrorCodes,
    ProfilesErrorCodes,
    UserErrorCodes,
]

class ErrorDetail(BaseModel):
    """Inner object that describes what went wrong."""
    code: str = Field(
        description="Machine-readable error code (e.g. USER_NOT_FOUND).",
        examples=[{
            enum_cls.__name__: {k: v.value for k, v in enum_cls.__members__.items()}
            for enum_cls in Error_codes
        }], # TODO:/ переделать, это вообще пиздец
    )
    message: str = Field(
        description="Human-readable description of the error.",
        examples=["User with this email not found"],
    )
    details: Any = Field(
        default=None,
        description="Optional structured payload with additional context "
                    "(e.g. validation field errors).",
    )


class ErrorResponse(BaseModel):
    success: bool = Field(default=False)
    error: ErrorDetail
    time: datetime = Field(
        description="Timestamp of when the error occurred (ISO 8601 format).",
        default_factory=datetime.now
    )

    @classmethod
    def of(
        cls,
        code: str,
        message: str,
        details: Any = None,
    ) -> "ErrorResponse":
        """Build an ``ErrorResponse`` from raw primitives."""
        return cls(error=ErrorDetail(code=code, message=message, details=details))

    @classmethod
    def internal(cls) -> "ErrorResponse":
        """Generic 500 response that deliberately hides internal details."""
        return cls.of(
            code="INTERNAL_SERVER_ERROR",
            message="An unexpected error occurred. Please try again later.",
        )
