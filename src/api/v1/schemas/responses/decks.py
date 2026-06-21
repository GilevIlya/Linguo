from datetime import datetime
from typing import List, Self
from uuid import UUID

from pydantic import BaseModel

from api.v1.utils.pagination import Pagination
from .base_response import BaseMessageResponse


class DeckSimpleView(BaseModel):
    """Simplified representation of a deck."""
    id_: UUID
    title: str
    description: str
    is_public: bool


class DeckWithStatsView(DeckSimpleView):
    """Deck representation for list endpoints with card statistics."""

    total_cards: int
    cards_to_learn: int


class DeckDetailedView(BaseModel):
    """Complete representation of a deck with timestamps."""
    id_: UUID
    title: str
    description: str
    is_public: bool
    created_at: datetime
    updated_at: datetime

class DeckActionResponse(BaseMessageResponse[DeckSimpleView]):
    """Response schema for successful deck action."""
    
    message: str

class DetailedDeckActionResponse(BaseMessageResponse[DeckDetailedView]):
    """Response schema for successful detailed deck action."""

    message: str


class RecentDecksResponse(BaseMessageResponse[list[DeckSimpleView]]):
    """Response schema for recently studied decks."""

    message: str

class DeckListWithPagination(BaseModel):
    data: List[DeckWithStatsView]
    total_decks: int
    current_page: int
    per_page: int
    pages: int
    has_next: bool
    has_previous: bool
    next_page: int | None
    previous_page: int | None

    @classmethod
    def from_pagination(cls, decks: list[DeckWithStatsView], pagination: Pagination) -> Self:
        return cls(
            data=decks,
            total_decks=pagination.total,
            current_page=pagination.current_page,
            per_page=pagination.per_page,
            pages=pagination.total_pages,
            has_next=pagination.has_next,
            has_previous=pagination.has_previous,
            next_page=pagination.next_page,
            previous_page=pagination.previous_page
        )