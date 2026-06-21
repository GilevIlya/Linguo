from datetime import datetime, timezone
from typing import TypeVar, Generic

from pydantic import BaseModel, Field, field_serializer

T = TypeVar("T")


class BaseMessageResponse(BaseModel, Generic[T]):
    """Base response for successful operations."""

    success: bool = True
    message: str
    data: T | None = None
    timestamp: datetime = Field(default_factory=lambda _: datetime.now(timezone.utc))

    @field_serializer("timestamp")
    def serialize_timestamp(self, v: datetime) -> str:
        return v.isoformat()


class PaginatedResponse(BaseModel):
    """Response with pagination."""
    total: int = 0
    page: int = 1
    page_size: int = 10
    pages: int = 0