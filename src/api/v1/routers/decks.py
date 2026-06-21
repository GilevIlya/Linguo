from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from api.v1.schemas.requests.decks_requests import CreateDeckRequest, UpdateDeckRequest
from api.v1.schemas.responses.decks import DeckListWithPagination, DeckActionResponse, DetailedDeckActionResponse, \
    RecentDecksResponse
from api.v1.services.decks_service import DecksService
from api.v1.utils.pagination import Pagination
from .security import get_current_user_id
from .utils.dependencies import get_deck_service

decks_router = APIRouter(
    prefix="/decks",
    tags=["decks"]
)


@decks_router.get(
    path="/recently-decks",
    summary="Get recently studied decks",
    response_model=RecentDecksResponse,
    description=(
        "Returns up to 3 unique decks with the latest user study activity. "
        "Decks are sorted by the most recent review timestamp in descending order."
    ),
)
async def get_recently_studied_decks(
        service: DecksService = Depends(get_deck_service),
        user_id: UUID = Depends(get_current_user_id),
) -> RecentDecksResponse:
    decks = await service.get_recently_studied_decks(actor_id=user_id)
    return RecentDecksResponse(
        message="Recently studied decks fetched successfully",
        data=decks,
    )

@decks_router.get("/decks/active")
async def get_active_decks(
        service: DecksService = Depends(get_deck_service),
        user_id: UUID = Depends(get_current_user_id),
        page: Annotated[int, Query(ge=1)] = 1
) -> DeckListWithPagination:
    decks, paginator = await service.get_paginated_active_decks_for_user(actor_id=user_id, page=page)
    return DeckListWithPagination.from_pagination(decks, paginator)

@decks_router.get(
    path="/{deck_id}",
    summary="Get a specific deck",
    response_model=DetailedDeckActionResponse,

    description=("""
        Retrieve detailed information about a specific deck belonging to the current user.

        The deck is identified by its unique ID.  
        Access is allowed only if the deck belongs to the authenticated user 
        or if the deck is public.
        """
    )
)
async def get_specific_deck(
        deck_id: UUID,
        user_id: UUID = Depends(get_current_user_id),
        service: DecksService = Depends(get_deck_service)
) -> DetailedDeckActionResponse:
    deck = await service.get_deck_details(
        actor_id=user_id,
        deck_id=deck_id
    )
    return DetailedDeckActionResponse(
        message="Deck successfully found",
        data=deck
    )



@decks_router.get(
    path="/",
    summary="Getting current user decks",
    response_model=DeckListWithPagination,

    description=("""
        Retrieve a paginated list of decks created by the authenticated user.

        Supports pagination via query parameters (e.g. page, size).  
        Returns basic information about each deck along with pagination metadata.
        """
    )
)
async def get_decks(
        name: str | None = Query(default=None, description="Filter decks by name (partial match)"),
        page: Annotated[int, Query(ge=1)] = 1,
        service: DecksService = Depends(get_deck_service),
        user_id: UUID = Depends(get_current_user_id)
) -> DeckListWithPagination:
    pagination: Pagination

    decks, pagination = await service.get_paginated_decks_for_user(
        name=name,
        actor_id=user_id,
        page=page
    )
    return DeckListWithPagination.from_pagination(
        decks, pagination
    )


@decks_router.post(
    path="/",
    summary="Deck Creation",
    response_model=DeckActionResponse,
    
    description=(
        "Creates a new deck for the authenticated user. "
        "The deck name must not be empty or contain only whitespace. "
        "Returns the created deck object with its generated ID and metadata."
    )
)
async def create_deck(
        data: CreateDeckRequest,
        service: DecksService = Depends(get_deck_service),
        user_id: UUID = Depends(get_current_user_id)
) -> DeckActionResponse:
    created_deck = await service.create_deck(
        actor_id=user_id,
        name=data.name,
        desc=data.description,
        is_public=data.is_public
    )
    return DeckActionResponse(
        message="Deck successfully created",
        data=created_deck,
    )


@decks_router.patch(
    path="/{deck_id}",
    summary="Deck update",
    response_model=DeckActionResponse,

    description=("""
        Partially updates a specific deck belonging to the current user.

        Only the fields provided in the request body will be updated. 
        Fields that are not included will remain unchanged.

        The deck must belong to the authenticated user, otherwise access will be denied.
        """
    )
)
async def update_deck(
        deck_id: UUID,
        payload: UpdateDeckRequest,
        service: DecksService = Depends(get_deck_service),
        user_id: UUID = Depends(get_current_user_id)
) -> DeckActionResponse:
    updated_deck = await service.update_deck(
        actor_id=user_id,
        deck_id=deck_id,
        new_name=payload.name,
        new_desc=payload.description,
        is_public=payload.is_public
    )
    return DeckActionResponse(
        message="Deck successfully updated",
        data=updated_deck
    )


@decks_router.delete(
    path="/{deck_id}",
    summary="Deck delete",
    response_model=DeckActionResponse,

    description=("""
        Partially updates a specific deck belonging to the current user.

        Only the fields provided in the request body will be updated. 
        Fields that are not included will remain unchanged.

        The deck must belong to the authenticated user, otherwise access will be denied.
        """
    )
)
async def delete_deck(
        deck_id: UUID,
        service: DecksService = Depends(get_deck_service),
        user_id: UUID = Depends(get_current_user_id),

) -> DeckActionResponse:
    deleted_deck = await service.delete_deck(
        actor_id=user_id,
        deck_id=deck_id
    )
    return DeckActionResponse(
        message="Deck successfully deleted",
        data=deleted_deck
    )