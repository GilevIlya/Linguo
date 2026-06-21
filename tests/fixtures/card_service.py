from unittest.mock import AsyncMock

import pytest

from api.v1.repositories.interfaces.ICardRepository import ICardRepository
from api.v1.repositories.interfaces.ICardReviewsRepository import ICardReviewsRepository
from api.v1.repositories.interfaces.IDeckRepository import IDeckRepository
from api.v1.services.card_service import CardService
from api.v1.services.file_service import FileService
from api.v1.services.interfaces.ICardReviewsService import ICardReviewsService
from api.v1.services.interfaces.IDeckService import IDeckService
from api.v1.services.interfaces.ISrsService import ISrsService
from api.v1.services.s3_service import S3Service
from api.v1.services.user_service import UserService


@pytest.fixture
def card_repository() -> AsyncMock:
    return AsyncMock(spec=ICardRepository)


@pytest.fixture
def deck_repository() -> AsyncMock:
    return AsyncMock(spec=IDeckRepository)


@pytest.fixture
def file_service_svc() -> AsyncMock:
    return AsyncMock(spec=FileService)

@pytest.fixture
def s3_svc() -> AsyncMock:
    return AsyncMock(spec=S3Service)

@pytest.fixture
def card_review_svc() -> AsyncMock:
    return AsyncMock(spec=ICardReviewsService)


@pytest.fixture
def card_svc(
    card_repository: AsyncMock,
    deck_repository: AsyncMock,
    card_review_svc: AsyncMock,
    file_service_svc: AsyncMock,
) -> CardService:
    return CardService(
        user_service=AsyncMock(spec=UserService),
        deck_service=AsyncMock(spec=IDeckService),
        file_service=file_service_svc,
        card_repository=card_repository,
        deck_repository=deck_repository,
        card_reviews_service=card_review_svc,
        card_reviews_repository=AsyncMock(ICardReviewsRepository),
        srs_service=AsyncMock(ISrsService),
    )
