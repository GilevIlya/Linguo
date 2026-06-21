import uuid
from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.models import User, Deck
from api.v1.repositories.card_repository import CardRepository
from api.v1.repositories.deck_repository import DeckRepository
from api.v1.repositories.interfaces.ICardReviewsRepository import ICardReviewsRepository
from api.v1.repositories.user_repository import UserRepository
from api.v1.services.card_service import CardService
from api.v1.services.file_service import FileService
from api.v1.services.interfaces.IDeckService import IDeckService
from api.v1.services.interfaces.ISrsService import ISrsService
from api.v1.services.user_service import UserService


@pytest.fixture
def card_repository(session: AsyncSession) -> CardRepository:
    return CardRepository(session)


@pytest.fixture
def deck_repository(session: AsyncSession) -> DeckRepository:
    return DeckRepository(session)


@pytest.fixture
def user_repository(session: AsyncSession) -> UserRepository:
    return UserRepository(session)


@pytest.fixture
def file_service_mock() -> AsyncMock:
    return AsyncMock(spec=FileService)


@pytest.fixture
def card_service(
    card_repository: CardRepository,
    deck_repository: DeckRepository,
    file_service_mock: AsyncMock,
    card_review_svc: AsyncMock,
) -> CardService:
    return CardService(
        user_service=AsyncMock(spec=UserService),
        deck_service=AsyncMock(spec=IDeckService),
        file_service=file_service_mock,
        card_repository=card_repository,
        deck_repository=deck_repository,
        card_reviews_service=card_review_svc,
        card_reviews_repository=AsyncMock(ICardReviewsRepository),
        srs_service=AsyncMock(ISrsService),
    )


@pytest.fixture
async def make_user(user_repository: UserRepository):
    async def _make(
        user_id: uuid.UUID | None = None,
        email: str | None = None,
    ) -> User:
        user_id = user_id or uuid.uuid4()
        email = email or f"{user_id}@test.com"
        user = User(id=user_id, email=email, password="hashed")
        return await user_repository.create(user)
    return _make


@pytest.fixture
async def make_deck(deck_repository: DeckRepository):
    async def _make(
        user_id: uuid.UUID,
        name: str = "Test Deck",
        description: str = "desc",
        is_public: bool = False,
        deck_id: uuid.UUID | None = None,
    ) -> Deck:
        deck = Deck(
            id=deck_id or uuid.uuid4(),
            user_id=user_id,
            name=name,
            description=description,
            is_public=is_public,
        )
        return await deck_repository.create(deck)
    return _make
