import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from api.v1.models.cards import Card
from api.v1.repositories.interfaces.ICardRepository import ICardRepository
from api.v1.services.builders.input_builders import TrueFalseInputBuilder
from api.v1.services.quiz_service import QuizService
from api.v1.services.schemas.input_contents import InputType
from api.v1.services.schemas.quizzes import InputTypeDTO


def _make_card(term: str = "apple") -> MagicMock:
    card = MagicMock(spec=Card)
    card.id = uuid.uuid4()
    card.deck_id = uuid.uuid4()
    card.term = term
    return card


class TestTrueFalseInputBuilder:
    async def test_is_available_returns_true_when_deck_has_two_or_more_cards(self):
        repo = AsyncMock(spec=ICardRepository)
        repo.count.return_value = 2
        builder = TrueFalseInputBuilder(repo)

        result = await builder.is_available(_make_card())

        assert result is True

    async def test_is_available_returns_false_when_deck_has_less_than_two_cards(self):
        repo = AsyncMock(spec=ICardRepository)
        repo.count.return_value = 1
        builder = TrueFalseInputBuilder(repo)

        result = await builder.is_available(_make_card())

        assert result is False

    async def test_build_returns_true_context_when_random_branch_is_true(self, monkeypatch):
        repo = AsyncMock(spec=ICardRepository)
        builder = TrueFalseInputBuilder(repo)
        card = _make_card(term="apple")
        monkeypatch.setattr("api.v1.services.builders.input_builders.random.choice", lambda _: True)

        result = await builder.build(card)

        assert result.type == InputType.TRUE_FALSE
        assert result.correct_answer == "true"
        assert result.content.statement == "apple"
        assert result.content.is_true is True
        repo.get_random_from_deck.assert_not_awaited()

    async def test_build_returns_false_context_with_distractor_when_random_branch_is_false(self, monkeypatch):
        repo = AsyncMock(spec=ICardRepository)
        builder = TrueFalseInputBuilder(repo)
        card = _make_card(term="apple")
        distractor = _make_card(term="banana")
        repo.get_random_from_deck.return_value = [distractor]
        monkeypatch.setattr("api.v1.services.builders.input_builders.random.choice", lambda _: False)

        result = await builder.build(card)

        assert result.type == InputType.TRUE_FALSE
        assert result.correct_answer == "false"
        assert result.content.statement == "banana"
        assert result.content.is_true is False
        repo.get_random_from_deck.assert_awaited_once_with(
            deck_id=card.deck_id,
            exclude_id=card.id,
            limit=1,
        )

    async def test_build_falls_back_to_true_context_when_no_distractors_found(self, monkeypatch):
        repo = AsyncMock(spec=ICardRepository)
        builder = TrueFalseInputBuilder(repo)
        card = _make_card(term="apple")
        repo.get_random_from_deck.return_value = []
        monkeypatch.setattr("api.v1.services.builders.input_builders.random.choice", lambda _: False)

        result = await builder.build(card)

        assert result.type == InputType.TRUE_FALSE
        assert result.correct_answer == "true"
        assert result.content.statement == "apple"
        assert result.content.is_true is True


class TestQuizServiceInputTypeMapping:
    @pytest.mark.parametrize(
        ("dto", "expected"),
        [
            (InputTypeDTO.TYPING, InputType.TYPING),
            (InputTypeDTO.MULTIPLE_CHOICE, InputType.MULTIPLE_CHOICE),
            (InputTypeDTO.FLASH_CARD, InputType.FLASH_CARD),
            (InputTypeDTO.TRUE_FALSE, InputType.TRUE_FALSE),
        ],
    )
    def test_map_input_type_maps_supported_values(self, dto: InputTypeDTO, expected: InputType):
        assert QuizService._map_input_type(dto) == expected

