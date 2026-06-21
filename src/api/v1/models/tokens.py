from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .basemodel import BaseModel
from .mixins.id_mixins import UUIDMixin

if TYPE_CHECKING:
    from .users import User


class Token(BaseModel, UUIDMixin):
    __tablename__ = "tokens"

    token = mapped_column(String(255), unique=True)
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    expired_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)

    user: Mapped["User"] = relationship(
        "User",
        lazy="selectin"
    )
