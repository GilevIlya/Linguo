from sqlalchemy.orm import DeclarativeBase

from .mixins.time_mixins import TimestampMixin


class BaseModel(DeclarativeBase, TimestampMixin):
    __abstract__ = True
