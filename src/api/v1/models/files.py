from uuid import UUID

from sqlalchemy import ForeignKey, String, BigInteger, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from .basemodel import BaseModel
from .mixins.id_mixins import UUIDMixin


class Files(BaseModel, UUIDMixin):
    __tablename__ = "files"

    owner_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), 
        index=True
    )
    file_key: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    original_name: Mapped[str] = mapped_column(String, nullable=False)
    extension: Mapped[str] = mapped_column(String(20), nullable=False)
    content_type: Mapped[str | None] = mapped_column(String, nullable=True)
    size_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True)