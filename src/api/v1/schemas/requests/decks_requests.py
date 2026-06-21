from pydantic import BaseModel, Field, field_validator
from api.v1.services.exceptions.base_exceptions import ValidationException


def validate_deck_name(value: str | None) -> str | None:
    if value is not None and not value.strip():
        raise ValidationException(
            error_code="DECK_NAME_EMPTY",
            message="Name cannot be empty or whitespace"
        )
    return value
"""Это проверка на сырые пробелы в поле name, я считаю что нет смысла выносить эту валидацию в сервис, хватит ограничения схемы"""


class CreateDeckRequest(BaseModel):
    name: str = Field(min_length=1, max_length=256)
    description: str | None = Field(default=None, max_length=512)
    is_public: bool = Field(default=False)

    @field_validator("name")
    def check_name(cls, value: str | None) -> str | None:
        return validate_deck_name(value)


class UpdateDeckRequest(BaseModel):
    name: str | None = Field(default=None, max_length=256)
    description: str | None = Field(default=None, max_length=512)
    is_public: bool | None = Field(default=None)

    @field_validator("name")
    def check_name(cls, value: str | None) -> str | None:
        return validate_deck_name(value)