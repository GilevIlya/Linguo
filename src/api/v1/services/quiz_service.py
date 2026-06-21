from datetime import datetime, timezone
from logging import getLogger
from uuid import UUID

from api.v1.configs.srs_config import srs_config
from api.v1.models.card_reviews import ReviewRating
from api.v1.repositories.interfaces.ICardReviewsRepository import ICardReviewsRepository
from api.v1.repositories.interfaces.IDeckRepository import IDeckRepository
from api.v1.repositories.interfaces.IReviewLogRepository import IReviewLogRepository
from api.v1.services.builders.question_builder import QuestionBuilder
from api.v1.services.exceptions.base_exceptions import BusinessLogicException, PermissionDeniedException, \
    NotFoundException
from api.v1.services.exceptions.error_codes.base import BaseErrorCodes
from api.v1.services.exceptions.error_codes.quiz_error_codes import QuizErrorCodes
from api.v1.services.interfaces.ICardService import ICardService
from api.v1.services.interfaces.ISrsService import ISrsService
from api.v1.services.schemas.input_contents import InputType
from api.v1.services.schemas.presentation import PresentationType
from api.v1.services.schemas.question import Question
from api.v1.services.schemas.quizzes import InputTypeDTO, PresentationTypeDTO

logger = getLogger("app")

class QuizService:
    __BUTTON_COEFFICIENT: float = 0.15 #TODO:/ вынести в конфиг

    def __init__(
            self,
            question_builder: QuestionBuilder,
            deck_repository: IDeckRepository,
            review_log_repository: IReviewLogRepository,
            card_service: ICardService,
            card_review_repository: ICardReviewsRepository,
            srs_service: ISrsService,
    ):
        self.deck_repository = deck_repository
        self.card_service = card_service
        self.card_review_repository = card_review_repository
        self.question_builder = question_builder
        self.srs = srs_service
        self.review_log_repository = review_log_repository

    async def get_next_question_by_deck(
            self,
            *,
            actor_id: UUID,
            deck_id: UUID,
            excepted_inputs: list[InputTypeDTO],
            excepted_presentations: list[PresentationTypeDTO],
    ) -> tuple[Question, UUID]:
        """Нужна для получения следующего вопроса для ревью. Выдает вопрос для карточки, которая просрочена дольше всего. Если карточек для ревью нет, кидает ошибку."""
        deck = await self.deck_repository.get_by_id(deck_id)
        if not deck:
            raise NotFoundException(
                BaseErrorCodes.RESOURCE_NOT_FOUND.value,
            )

        if deck.user_id != actor_id:
            logger.warning("User %s tried to access deck %s that doesn't belong to them", actor_id, deck_id)
            raise PermissionDeniedException(
                BaseErrorCodes.PERMISSION_DENIED.value,
            )

        card_review = await self.card_review_repository.get_most_overdue_card(deck_id)
        if not card_review:
            raise BusinessLogicException(
                QuizErrorCodes.THERE_IS_NO_CARD_TO_REVIEW.value,
                "All reviews already made",
            )

        inputs = map(self._map_input_type, excepted_inputs) #Filters
        presentations = map(self._map_presentation_type, excepted_presentations)

        return (
            await self.question_builder.build_random(
                card_review.card,
                excepted_presentations=list(presentations),
                excepted_inputs=list(inputs),
            ),
            card_review.id
        )

    async def rate_question(self, actor_id: UUID, review_card_id: UUID, rating: int, current_datetime: datetime, review_duration: int):
        """Нужна для оценки ответа пользователя и обновления card_review"""
        logger.info("Rating question for user %s, review_card_id %s, rating %s", actor_id, review_card_id, rating)

        card_review = await self.card_review_repository.get_for_user(user_id=actor_id, card_review_id=review_card_id)

        if not card_review or card_review.due > datetime.now(timezone.utc):
            logger.info("Card review %s for user %s is not due yet or doesn't exist", review_card_id, actor_id)
            raise NotFoundException(
                BaseErrorCodes.RESOURCE_NOT_FOUND.value,
                "You have nothing to learn right now or the review card doesn't exist",
            )

        rating = self._prepare_rating(rating, self.srs.get_card_retrievability(card_review, current_datetime))

        review_result = self.srs.review_card(
            card_review=card_review,
            rating=rating,
            review_time=current_datetime,
            review_duration=review_duration
        )
        await self.review_log_repository.create(review_result.review_log)
        await self.card_review_repository.update(card_review, review_result.card_review.to_dict())



    def _prepare_rating(self, rating: int, retrievability: float) -> ReviewRating:
        """
        Look at the 'retrievability' at the moment of clicking:

        ```
        R ≤ (desired_retention - 0.15)  →  Again
        R >  (desired_retention - 0.15)  →  Good
        ```

        Meaning: I remembered **on time** → 'Good'. I remembered **strongly after the term** → 'Again'.

        The user doesn't think about it — he just clicks "I know".

        > For new cards (retrievability not defined) → always 'Again'
        """
        if rating < 1 or rating > 3:
            raise BusinessLogicException(
                QuizErrorCodes.INVALID_RATING.value,
                "Rating must be between 1 and 3",
            )
        if retrievability is None or retrievability == 0:  # new card, not reviewed before
            return ReviewRating.AGAIN
        elif retrievability <= (srs_config.DESIRED_RETENTION - self.__BUTTON_COEFFICIENT):
            return ReviewRating.AGAIN
        else:
            return ReviewRating.GOOD


    @staticmethod
    def _map_input_type(dto: InputTypeDTO):
        match dto:
            case InputTypeDTO.TYPING:
                return InputType.TYPING
            case InputTypeDTO.MULTIPLE_CHOICE:
                return InputType.MULTIPLE_CHOICE
            case InputTypeDTO.FLASH_CARD:
                return InputType.FLASH_CARD
            case InputTypeDTO.TRUE_FALSE:
                return InputType.TRUE_FALSE
            case _:
                raise BusinessLogicException(
                    QuizErrorCodes.INVALID_FIELD_TYPE.value,
                    "Invalid input type",
                )

    @staticmethod
    def _map_presentation_type(dto: PresentationTypeDTO):
        match dto:
            case PresentationTypeDTO.CLOZE:
                return PresentationType.CLOZE
            case PresentationTypeDTO.IMAGE:
                return PresentationType.IMAGE
            case PresentationTypeDTO.SOUND:
                return PresentationType.SOUND
            case PresentationTypeDTO.DEFINITION:
                return PresentationType.DEFINITION
            case _:
                raise BusinessLogicException(
                    QuizErrorCodes.INVALID_FIELD_TYPE.value,
                    "Invalid presentation type",
                )
