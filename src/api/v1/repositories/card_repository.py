from datetime import datetime, timezone
from typing import override
from uuid import UUID

from sqlalchemy import select, exists, or_, update, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.models.cards import Card
from api.v1.repositories.interfaces.ICardRepository import ICardRepository, CardsWithStats
from .sqlalchemy_repository import SQLAlchemyBaseRepository
from ..models import Deck, CardReview


class CardRepository(SQLAlchemyBaseRepository[Card, UUID], ICardRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Card)
    
    async def find_by_deck_id(self, deck_id: UUID, limit: int = 50, offset: int = 0) -> list[Card]:
        stmt = (
            select(self.model)
            .where(
                self.model.deck_id == deck_id,
                self.model.deleted_at.is_(None)
            )
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    @override
    async def find_by_deck_id_with_stats(
        self,
        deck_id: UUID,
        limit: int = 50,
        offset: int = 0,
        filter: str | None = None,
    ) -> list[CardsWithStats]:
        where_clauses = [
            Card.deck_id == deck_id,
            Card.deleted_at.is_(None)
        ]

        if filter:
            where_clauses.append(or_(Card.term.ilike(f"%{filter}%"), Card.definition.ilike(f"%{filter}%")))

        stmt = (
            select(
                Card.id,
                Card.term,
                Card.definition,
                Card.deck_id,
                CardReview.due,
                CardReview.last_review,
                Card.created_at,
            )
            .select_from(Card)
            .join(
                CardReview,
                and_(
                    CardReview.card_id == Card.id,
                    CardReview.deleted_at.is_(None)
                )
            )
            .where(
                *where_clauses
            )
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)

        return [
            CardsWithStats(
                id_=row.id,
                term=row.term,
                def_=row.definition,
                deck_id=row.deck_id,
                next_review=row.due,
                last_review=row.last_review,
                created_at=row.created_at
            )
            for row in result.all()
        ]


    @override
    async def delete_if_owned_by(self, card_id: UUID, user_id: UUID) -> Card | None:
        stmt = (
            update(Card)
            .where(
                Card.id == card_id,
                Card.deleted_at.is_(None),
                exists(
                    select(1).where(
                        Deck.id == Card.deck_id,
                        Deck.user_id == user_id,
                    )
                ),
            )
            .values(deleted_at=datetime.now(timezone.utc))
            .returning(Card)
        )

        result = await self.session.execute(stmt)
        await self.session.commit()

        return result.scalar_one_or_none()

        """Ниже реализация с фактическим удалением из базы"""
        # stmt = (
        #     delete(Card)
        #     .where(
        #         Card.id == card_id,
        #         exists(
        #             select(1).where(
        #                 Deck.id == Card.deck_id,
        #                 Deck.user_id == user_id,
        #             )
        #         ),
        #     )
        #     .returning(Card)
        # )
        # result = await self.session.execute(stmt)
        # await self.session.commit()
        # return result.scalar_one_or_none()


    @override
    async def get_owned_by_user(self, card_id: UUID, user_id: UUID) -> Card | None:
        stmt = select(self.model).where(
            self.model.id == card_id,
            self.model.deleted_at.is_(None),
            exists(
                select(1).where(
                    Deck.id == self.model.deck_id,
                    or_(
                        Deck.user_id == user_id,
                        Deck.is_public
                    ),
                )
            ),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    @override
    async def get_random_from_deck(self, deck_id: UUID, exclude_id: UUID, limit=3) -> list[Card]:
        stmt = (
            select(self.model)
            .where(
                self.model.deck_id == deck_id,
                self.model.id != exclude_id
            )
            .order_by(func.random())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    @override
    async def count_by_deck(self, deck_id: UUID, filter: str | None) -> int:
        where_clauses = [
            Card.deck_id == deck_id,
            Card.deleted_at.is_(None)
        ]

        if filter:
            where_clauses.append(or_(Card.term.ilike(f"%{filter}%"), Card.definition.ilike(f"%{filter}%")))

        stmt = (
            select(func.count())
            .where(
                *where_clauses,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()
