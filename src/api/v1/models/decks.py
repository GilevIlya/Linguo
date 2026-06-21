from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .basemodel import BaseModel
from .mixins.id_mixins import UUIDMixin

if TYPE_CHECKING:
    from .users import User

class Deck(BaseModel, UUIDMixin):
    __tablename__ = "decks"

    name: Mapped[str]
    description: Mapped[str]
    is_public: Mapped[bool] = mapped_column(default=False)
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )

    user: Mapped["User"] = relationship(
        "User",
        lazy="noload"
    )
