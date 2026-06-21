import random
from typing import override

from .base import IInputBuilder
from ..schemas.input import InputContext
from ..schemas.input_contents import (
    InputFlashCardContent,
    InputMultipleChoiceContent,
    InputType,
    InputTypingContent,
    InputTrueFalseContent,
)
from ...models import Card
from ...repositories.interfaces.ICardRepository import ICardRepository


class TypingInputBuilder(IInputBuilder):
    TYPE = InputType.TYPING

    @override
    async def build(self, card: Card) -> InputContext:
        return InputContext(correct_answer=card.term, content=InputTypingContent())

    @override
    async def is_available(self, card: Card) -> bool:
        return True  # always available


class FlashCardInputBuilder(IInputBuilder):
    TYPE = InputType.FLASH_CARD

    @override
    async def build(self, card: Card) -> InputContext:
        return InputContext(correct_answer=card.term, content=InputFlashCardContent())

    @override
    async def is_available(self, card: Card) -> bool:
        return True


class MultiChoiceInputBuilder(IInputBuilder):
    MIN_CARDS_FOR_MULTIPLE_CHOICE: int = 4
    TYPE = InputType.MULTIPLE_CHOICE

    def __init__(self, cards_repo: ICardRepository):
        self.cards_repo = cards_repo

    @override
    async def is_available(self, card: Card) -> bool:
        return await self.cards_repo.count(
            {"deck_id": card.deck_id}) >= self.MIN_CARDS_FOR_MULTIPLE_CHOICE  # нужно хотя бы 4 карточки в колоде (1 правильный ответ + 3 отвлекающих)

    @override
    async def build(self, card: Card) -> InputContext:
        distractors = await self.cards_repo.get_random_from_deck(
            deck_id=card.deck_id,
            exclude_id=card.id,
            limit=self.MIN_CARDS_FOR_MULTIPLE_CHOICE - 1
        )
        options = [d.term for d in distractors] + [card.term]
        random.shuffle(options)
        return InputContext(
            correct_answer=card.term,
            content=InputMultipleChoiceContent(
                values=options,
            )
        )


class TrueFalseInputBuilder(IInputBuilder):
    MIN_CARDS_FOR_TRUE_FALSE: int = 2
    TYPE = InputType.TRUE_FALSE

    def __init__(self, cards_repo: ICardRepository):
        self.cards_repo: ICardRepository = cards_repo

    @override
    async def is_available(self, card: Card) -> bool:
        return await self.cards_repo.count({"deck_id": card.deck_id}) >= self.MIN_CARDS_FOR_TRUE_FALSE

    @override
    async def build(self, card: Card) -> InputContext:
        should_use_true_statement = random.choice([True, False])

        if should_use_true_statement:
            return self._build_true_context(card)

        distractors = await self.cards_repo.get_random_from_deck(
            deck_id=card.deck_id,
            exclude_id=card.id,
            limit=1
        )
        if not distractors:
            return self._build_true_context(card)

        distractor = distractors[0]
        return InputContext(
            correct_answer="false",
            content=InputTrueFalseContent(statement=distractor.term, is_true=False)
        )

    @staticmethod
    def _build_true_context(card: Card) -> InputContext:
        return InputContext(
            correct_answer="true",
            content=InputTrueFalseContent(statement=card.term, is_true=True),
        )

