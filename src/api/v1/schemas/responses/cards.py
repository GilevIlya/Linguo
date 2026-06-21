from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel

from api.v1.schemas.responses.base_response import BaseMessageResponse, PaginatedResponse


class AdditionalFieldView(BaseModel):
    """Representation of a card's additional field (image, audio, context, synonyms)."""
    type_: str
    content: Any


class CardSimpleView(BaseModel):
    """Simplified representation of a card."""
    id_: UUID
    term: str
    def_: str
    deck_id: UUID


class CardDetailedView(BaseModel):
    """Complete representation of a card with all additional fields."""
    id_: UUID
    term: str
    def_: str
    deck_id: UUID
    additional_fields: tuple[AdditionalFieldView, ...]
    created_at: datetime
    updated_at: datetime

class CardDetailedViewWithStats(CardDetailedView):
    """Detailed representation of a card including review statistics."""
    next_review: datetime
    last_review: datetime | None
    retrievability: float

class CardCreationResponse(BaseMessageResponse[CardSimpleView]):
    """Response schema for successful card creation."""
    message: str = "Card created successfully"

class CardUpdatingResponse(BaseMessageResponse[CardDetailedView]):
    """Response schema for successful card updating."""
    message: str = "Card updated successfully"

class CardDeckChangingResponse(BaseMessageResponse[CardSimpleView]):
    """Response schema for successful card deck changing."""
    message: str = "Card moved to new deck successfully"

class CardViewResponse(BaseMessageResponse[CardDetailedViewWithStats]):
    """Response schema for retrieving a card's details with statistic."""
    message: str = "Card retrieved successfully"

class CardSimpleViewWithStats(CardSimpleView):
    """Simplified representation of a card including review statistics."""
    next_review: datetime
    last_review: datetime | None
    created_at: datetime


class CardsListResponse(BaseMessageResponse[tuple[CardSimpleViewWithStats, ...]], PaginatedResponse):
    """Response schema for retrieving a list of cards."""
    message: str = "Cards retrieved successfully"

class CountUntouchedCardsResponse(BaseMessageResponse[int]):
    """Response schema for retrieving the count of untouched cards in a deck."""
    message: str = "Count of untouched cards retrieved successfully"

