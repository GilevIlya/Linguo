from logging import getLogger
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Form, UploadFile, Query
from starlette import status

from api.v1.services.card_service import CardService
from .security import get_current_user_id
from .utils.dependencies import get_card_service, get_card_reviews_service
from ..schemas.responses.base_response import PaginatedResponse
from ..schemas.responses.cards import CardCreationResponse, CardUpdatingResponse, CardDeckChangingResponse, \
    CardViewResponse, CardsListResponse, CountUntouchedCardsResponse
from ..services.interfaces.ICardReviewsService import ICardReviewsService
from ..services.schemas.file_param import FileParam
from ..utils.pagination import Pagination

logger = getLogger("app")

cards_router = APIRouter(
    prefix="/cards",
    tags=["cards"],
)


@cards_router.post("/{deck_id}", status_code=status.HTTP_201_CREATED, response_model=CardCreationResponse)
async def create_card(
        deck_id: UUID,
        term: Annotated[str, Form()],
        definition: Annotated[str, Form()],
        context: Annotated[str | None, Form()] = None,
        image: UploadFile | None = None,
        audio: UploadFile | None = None,
        user_id: UUID = Depends(get_current_user_id),
        card_service: CardService = Depends(get_card_service),
):
    card_view = await card_service.create_card(
        actor_id=user_id,
        deck_id=deck_id,
        term=term,
        def_=definition,
        image=FileParam(content=image.file, content_type=image.content_type, original_name=image.filename, size=image.size) if image else None,
        sound=FileParam(content=audio.file, content_type=audio.content_type, original_name=audio.filename, size=audio.size) if audio else None,
        context=context
    )
    return CardCreationResponse(data=card_view)


@cards_router.delete("/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_card(
        card_id: UUID,
        user_id: UUID = Depends(get_current_user_id),
        card_service: CardService = Depends(get_card_service),
):
    await card_service.delete_card(actor_id=user_id, id_=card_id)


@cards_router.patch("/{card_id}", status_code=status.HTTP_202_ACCEPTED, response_model=CardUpdatingResponse)
async def update_card(
        card_id: UUID,
        term: Annotated[str | None, Form()] = None,
        definition: Annotated[str | None, Form()] = None,
        context: Annotated[str | None, Form()] = None,
        image: UploadFile | None = None,
        audio: UploadFile | None = None,
        user_id: UUID = Depends(get_current_user_id),
        card_service: CardService = Depends(get_card_service),
):
    logger.info(image.content_type if image else "No image provided")
    card_view = await card_service.update_card(
        actor_id=user_id,
        card_id=card_id,
        term=term,
        def_=definition,
        image=FileParam(content=image.file, content_type=image.content_type, original_name=image.filename, size=image.size) if image else None,
        sound=FileParam(content=audio.file, content_type=audio.content_type, original_name=audio.filename, size=audio.size) if audio else None,
        context=context
    )
    return CardUpdatingResponse(data=card_view)


@cards_router.put("/{card_id}", status_code=status.HTTP_202_ACCEPTED, response_model=CardDeckChangingResponse)
async def change_card_deck(
        card_id: UUID,
        new_deck_id: UUID,
        user_id: UUID = Depends(get_current_user_id),
        card_service: CardService = Depends(get_card_service),
):
    card_view = await card_service.change_card_deck(actor_id=user_id, card_id=card_id, new_deck_id=new_deck_id)
    return CardDeckChangingResponse(data=card_view)

@cards_router.get("/{card_id}", status_code=status.HTTP_200_OK, response_model=CardViewResponse)
async def get_card_details(
        card_id: UUID,
        user_id: UUID = Depends(get_current_user_id),
        card_service: CardService = Depends(get_card_service),
):
    card_view = await card_service.get_card_details(actor_id=user_id, card_id=card_id)
    return CardViewResponse(data=card_view)


@cards_router.get("/cards/{deck_id}/total", status_code=status.HTTP_200_OK, response_model=CardsListResponse)
async def get_cards_in_deck(
        deck_id: UUID,
        page: int = 1,
        q: str | None = Query(default=None, description="Filter cards by term and definition (partial match)"),
        user_id: UUID = Depends(get_current_user_id),
        card_service: CardService = Depends(get_card_service),
):
    count = await card_service.count_cards_in_deck(actor_id=user_id, deck_id=deck_id, filter=q)
    pagination = Pagination(total=count, current_page=page)

    cards_list_view = await card_service.get_cards_by_deck(
        actor_id=user_id,
        deck_id=deck_id,
        limit=pagination.per_page,
        offset=pagination.start,
        filter=q,
    )

    pagination_response = PaginatedResponse(
        total=pagination.total,
        page=pagination.current_page,
        page_size=pagination.per_page,
        pages=pagination.total_pages,
    )
    return CardsListResponse(
        data=cards_list_view,
        **pagination_response.model_dump()
    )


@cards_router.get("/count-untouched/{deck_id}", status_code=status.HTTP_200_OK, response_model=CountUntouchedCardsResponse)
async def count_untouched_cards_in_deck(
        deck_id: UUID,
        user_id: UUID = Depends(get_current_user_id),
        card_service: ICardReviewsService = Depends(get_card_reviews_service),
):
    count = await card_service.count_untouched_cards_by_deck(actor_id=user_id, deck_id=deck_id)
    return CountUntouchedCardsResponse(data=count)
