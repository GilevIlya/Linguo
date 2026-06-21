from datetime import datetime, timezone
from typing import override
from uuid import UUID

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from .interfaces.ICardReviewsRepository import ICardReviewsRepository
from .sqlalchemy_repository import SQLAlchemyBaseRepository
from ..models import CardReview, Card, Deck


class CardReviewsRepository(SQLAlchemyBaseRepository[CardReview, UUID], ICardReviewsRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, CardReview)

    @override
    async def get_most_overdue_card(self, deck_id: UUID) -> CardReview | None:
        now = datetime.now(timezone.utc)
        stmt = (
            select(CardReview)
            .join(Card, and_(CardReview.card_id == Card.id, Card.deleted_at.is_(None)))
            .where(
                Card.deck_id == deck_id,
                CardReview.due <= now,
                CardReview.deleted_at.is_(None),
                )
            .options(joinedload(CardReview.card))  # подгрузит card за один запрос и потом можно card_review.card.term и т.д. без дополнительных запросов
            .order_by(CardReview.due.asc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    @override
    async def count_expired_reviews_by_deck(self, deck_id: UUID) -> int:
        now = datetime.now(timezone.utc)
        stmt = (
            select(func.count()).select_from(CardReview)
            .join(Card, and_(CardReview.card_id == Card.id, Card.deleted_at.is_(None)))
            .where(
                Card.deck_id == deck_id,
                CardReview.due <= now,
                CardReview.deleted_at.is_(None),
                )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get_for_user(self, user_id: UUID, card_review_id: UUID) -> CardReview | None:
        stmt = (
            select(CardReview)
            .join(Card, and_(
                Card.id == CardReview.card_id,
                Card.deleted_at.is_(None),
            ))
            .join(Deck, and_(
                Deck.id == Card.deck_id,
                Deck.deleted_at.is_(None),
            ))
            .where(
                CardReview.id == card_review_id,
                CardReview.deleted_at.is_(None),
                Deck.user_id == user_id,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    @override
    async def get_by_card_id(self, card_id: UUID) -> CardReview | None:
        stmt = (
            select(CardReview)
            .where(
                CardReview.card_id == card_id,
                CardReview.deleted_at.is_(None),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    @override
    async def count_untouched_cards_by_deck_id(self, deck_id: UUID) -> int:
        stmt = (
            select(func.count()).select_from(Card)
            .join(CardReview, and_(
                Card.id == CardReview.card_id,
                CardReview.deleted_at.is_(None),
            ))
            .where(
                Card.deck_id == deck_id,
                Card.deleted_at.is_(None),
                CardReview.last_review.is_(None),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()
