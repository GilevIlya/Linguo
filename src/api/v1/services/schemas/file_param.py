from dataclasses import dataclass
from logging import getLogger
from typing import BinaryIO

from api.v1.services.exceptions.base_exceptions import BusinessLogicException
from api.v1.services.exceptions.error_codes.card_error_codes import CardErrorCodes

logger = getLogger("app")

@dataclass(frozen=True)
class FileParam:
    ALLOWED_CONTENT_TYPES = ("image/", "audio/", )

    content: BinaryIO
    content_type: str | None
    original_name: str | None = ""
    size: int | None = None

    def __post_init__(self):
        if not self.content_type or not self.content_type.startswith(self.ALLOWED_CONTENT_TYPES):
            logger.warning("Invalid file type: %s", self.content_type)
            raise BusinessLogicException(
                error_code=CardErrorCodes.INVALID_FILE_TYPE.value,
                message="Only image and audio files are allowed"
            )

    @property
    def is_image(self) -> bool:
        return self.content_type is not None and self.content_type.startswith("image/")

    @property
    def is_audio(self) -> bool:
        return self.content_type is not None and self.content_type.startswith("audio/")

    @property
    def file_extension(self) -> str:
        if self.content_type:
            return self.content_type.split("/")[-1]
        return "bin"