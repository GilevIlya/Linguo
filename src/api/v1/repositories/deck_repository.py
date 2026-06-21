from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import and_, func, select, case
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.models import Card, CardReview
from api.v1.models.decks import Deck
from api.v1.repositories.interfaces.IDeckRepository import ActiveDeckMetrics, IDeckRepository
from .sqlalchemy_repository import SQLAlchemyBaseRepository


class DeckRepository(SQLAlchemyBaseRepository[Deck, UUID], IDeckRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Deck)
    
    async def find_by_user_id(self, user_id: UUID, limit: int = 50, offset: int = 0) -> list[Deck]:
        stmt = (
            select(self.model)
            .where(
                self.model.user_id == user_id,
                self.model.deleted_at.is_(None),)
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def update(self, obj: Deck, data: dict[str, Any]) -> Deck:
        for key, value in data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)

        await self.session.commit()
        await self.session.refresh(obj)
        return obj
    
    async def soft_delete(self, obj: Deck) -> Deck:
        obj.deleted_at = datetime.now(timezone.utc)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def find_recently_studied_by_user_id(self, user_id: UUID, limit: int = 3) -> list[Deck]:
        if limit <= 0: # TODO:/ говнозапрос: разбить на подзапросы
            return []

        max_reviewed_at = func.max(CardReview.last_review)
        recent_decks_subquery = (
            select(
                Card.deck_id.label("deck_id"),
                max_reviewed_at.label("max_reviewed_at"),
            )
            .join(Card, and_(CardReview.card_id == Card.id, Card.deleted_at.is_(None)))
            .join(Deck, and_(Deck.id == Card.deck_id, Deck.deleted_at.is_(None)))
            .where(
                CardReview.deleted_at.is_(None),
                CardReview.last_review.is_not(None),
                Deck.user_id == user_id,
            )
            .group_by(Card.deck_id)
            .order_by(max_reviewed_at.desc())
            .limit(limit)
            .subquery()
        )

        stmt = (
            select(Deck)
            .join(recent_decks_subquery, Deck.id == recent_decks_subquery.c.deck_id)
            .order_by(recent_decks_subquery.c.max_reviewed_at.desc())
        )

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_user_id_with_stats(
        self,
        user_id: UUID,
        name: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[ActiveDeckMetrics]:
        now = datetime.now(timezone.utc)
        deck_conditions = [
            Deck.user_id == user_id,
            Deck.deleted_at.is_(None)
        ]

        if name:
            deck_conditions.append(Deck.name.ilike(f"%{name}%"))

        paginated_decks_cte = (
            select(Deck.id)
            .where(*deck_conditions)  # <-- Распаковываем наши условия
            .order_by(Deck.created_at.desc(), Deck.id.asc())
            .offset(offset)
            .limit(limit)
            .cte("paginated_decks")
        )

        stmt = (
            select(
                Deck,
                func.count(Card.id.distinct()).label("total_cards"),
                func.count(
                    case(
                        (CardReview.due <= now, CardReview.card_id),
                        else_=None
                    ).distinct()
                ).label("cards_to_learn"),
            )
            .join(paginated_decks_cte, Deck.id == paginated_decks_cte.c.id)
            .outerjoin(Card, and_(Card.deck_id == Deck.id, Card.deleted_at.is_(None)))
            .outerjoin(CardReview, and_(CardReview.card_id == Card.id, CardReview.deleted_at.is_(None)))
            .group_by(Deck.id)
            .order_by(Deck.created_at.desc(), Deck.id.asc())  # Возвращаем порядок из CTE
        )

        result = await self.session.execute(stmt)

        return [
            ActiveDeckMetrics(
                deck=row.Deck,
                total_cards=row.total_cards,
                cards_to_learn=row.cards_to_learn,
            )
            for row in result
        ]

    async def find_active_by_user_id_with_metrics(
        self,
        user_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> list[ActiveDeckMetrics]:
        now = datetime.now(timezone.utc)

        due_cards_subquery = (
            select(CardReview.card_id.label("card_id"))
            .where(
                CardReview.deleted_at.is_(None),
                CardReview.due <= now,
            )
            .subquery()
        )

        cards_to_learn_count = func.count(due_cards_subquery.columns.card_id)

        stmt = (
            select(
                Deck,
                func.count(Card.id).label("total_cards"),
                cards_to_learn_count.label("cards_to_learn"),
            )
            .join(Card, and_(Card.deck_id == Deck.id, Card.deleted_at.is_(None)))
            .outerjoin(due_cards_subquery, due_cards_subquery.columns.card_id == Card.id) # нужно что бы у нас посчитало total_cards, если будет просто left join то просроченые не посчитаются в total_cards, а так мы сначала посчитали total_cards
            .where(
                Deck.user_id == user_id,
                Deck.deleted_at.is_(None),
            )
            .group_by(Deck.id, Deck.name)
            .having(cards_to_learn_count > 0)
            .order_by(cards_to_learn_count.desc(), Deck.name.asc(), Deck.id.asc())
            .offset(offset)
            .limit(limit)
        )

        result = await self.session.execute(stmt)
        return [
            ActiveDeckMetrics( #TODO поменять хуйню
                deck=row["Deck"],
                total_cards=row["total_cards"],
                cards_to_learn=row["cards_to_learn"],
            )
            for row in result.mappings()
        ]

