from uuid import UUID

from sqlalchemy import ForeignKey, TypeDecorator
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import Mapped, mapped_column

from .basemodel import BaseModel
from .mixins.id_mixins import UUIDMixin
from .types.additional_fields import AdditionalField, AdditionalFieldType


class AdditionalFieldsJSON(TypeDecorator):
    """Автоматически конвертирует список словарей в список объектов AdditionalField"""
    impl = JSONB
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None

        return [
            {"type": field.type.value, "content": field.content}
            for field in value
        ]

    def process_result_value(self, value, dialect):
        if value is None:
            return None

        return [
            AdditionalField(
                type=AdditionalFieldType(field["type"]),
                content=field["content"],
            )
            for field in value
        ]


class Card(BaseModel, UUIDMixin):
    __tablename__ = "cards"

    term: Mapped[str]
    definition: Mapped[str]
    deck_id: Mapped[UUID] = mapped_column(
        ForeignKey("decks.id", ondelete="CASCADE"),
        index=True
    )
    additional_fields: Mapped[list[AdditionalField]] =  mapped_column(
        MutableList.as_mutable(AdditionalFieldsJSON),
        default=list,
    )
