from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .basemodel import BaseModel
from .mixins.id_mixins import UUIDMixin

from .files import Files

from uuid import UUID


class Profile(BaseModel, UUIDMixin):
    __tablename__ = "profiles"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), 
        index=True
    )
    username: Mapped[str] = mapped_column(String(55), unique=True)
    bio: Mapped[str] = mapped_column(nullable=True)

    avatar_file_key: Mapped[str | None] = mapped_column(
        ForeignKey("files.file_key", ondelete="SET NULL"),
        nullable=True
    )

    avatar: Mapped["Files"] = relationship(
        "Files",
        foreign_keys=[avatar_file_key],
        lazy="joined"
    )