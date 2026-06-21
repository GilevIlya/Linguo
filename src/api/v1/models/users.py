from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from .basemodel import BaseModel
from .mixins.id_mixins import UUIDMixin


class User(BaseModel, UUIDMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True)
    password: Mapped[str] = mapped_column(String(255))
