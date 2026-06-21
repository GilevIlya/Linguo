import uuid

from sqlalchemy.orm import Mapped, mapped_column, declared_attr


class UUIDMixin:
    @declared_attr
    def id(cls) -> Mapped[uuid.UUID]:
        return mapped_column(
            primary_key=True,
            default=uuid.uuid4,
        )