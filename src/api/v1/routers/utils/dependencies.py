from functools import lru_cache
from typing import Annotated

from aioboto3 import Session as S3Session  # type: ignore
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.configs.db_config import get_session
from api.v1.repositories.FeedbackRepository import FeedbackRepository
from api.v1.repositories.card_repository import CardRepository
from api.v1.repositories.card_reviews_repository import CardReviewsRepository
from api.v1.repositories.deck_repository import DeckRepository
from api.v1.repositories.file_repository import FileRepository
from api.v1.repositories.interfaces.ICardRepository import ICardRepository
from api.v1.repositories.interfaces.ICardReviewsRepository import ICardReviewsRepository
from api.v1.repositories.interfaces.IDeckRepository import IDeckRepository
from api.v1.repositories.interfaces.IFeedbackRepository import IFeedbackRepository
from api.v1.repositories.interfaces.IFileRepository import IFileRepository
from api.v1.repositories.interfaces.IProfileRepository import IProfileRepository
from api.v1.repositories.interfaces.IReviewLogRepository import IReviewLogRepository
from api.v1.repositories.interfaces.ITokenRepository import ITokenRepository
from api.v1.repositories.interfaces.IUserRepository import IUserRepository
from api.v1.repositories.profile_repository import ProfileRepository
from api.v1.repositories.review_log_repository import ReviewLogRepository
from api.v1.repositories.token_repository import TokenRepository
from api.v1.repositories.user_repository import UserRepository
from api.v1.services.FeedbackService import FeedbackService
from api.v1.services.FsrsService import FsrsService
from api.v1.services.auth_service import AuthService
from api.v1.services.builders.builder_registry import InputBuilderRegistry, PresentationBuilderRegistry
from api.v1.services.builders.compatibility_registry import CompatibilityRegistry
from api.v1.services.builders.input_builders import FlashCardInputBuilder, TypingInputBuilder, TrueFalseInputBuilder, \
    MultiChoiceInputBuilder
from api.v1.services.builders.presentation_builders import DefinitionPresentationBuilder, ImagePresentationBuilder, \
    SoundPresentationBuilder, ClozePresentationBuilder
from api.v1.services.builders.question_builder import QuestionBuilder
from api.v1.services.card_reviews_service import CardReviewsService
from api.v1.services.card_service import CardService
from api.v1.services.decks_service import DecksService
from api.v1.services.file_service import FileService
from api.v1.services.interfaces.ICardReviewsService import ICardReviewsService
from api.v1.services.interfaces.ICardService import ICardService
from api.v1.services.interfaces.ISrsService import ISrsService
from api.v1.services.ml_service import MLService
from api.v1.services.profile_service import ProfileService
from api.v1.services.quiz_service import QuizService
from api.v1.services.s3_service import S3Service
from api.v1.services.schemas.input_contents import InputType
from api.v1.services.schemas.presentation import PresentationType
from api.v1.services.tokens_service import TokenService
from api.v1.services.user_service import UserService


def get_user_repository(session: Annotated[AsyncSession, Depends(get_session)]) -> IUserRepository:
    return UserRepository(session)

@lru_cache
def get_ml_service() -> MLService:
    return MLService()

def get_token_repository(session: Annotated[AsyncSession, Depends(get_session)]) -> ITokenRepository:
    return TokenRepository(session)


def get_deck_repository(session: Annotated[AsyncSession, Depends(get_session)]) -> IDeckRepository:
    return DeckRepository(session)

def get_profile_repository(session: Annotated[AsyncSession, Depends(get_session)]) -> IProfileRepository:
    return ProfileRepository(session)

def get_token_service(repo: Annotated[ITokenRepository, Depends(get_token_repository)]):
    return TokenService(repo)


def get_user_service(repo: Annotated[IUserRepository, Depends(get_user_repository)]):
    return UserService(repo)

def get_feedback_repository(session: Annotated[AsyncSession, Depends(get_session)]) -> IFeedbackRepository:
    return FeedbackRepository(session)

def get_feedback_service(
        feedback_repository: Annotated[IFeedbackRepository, Depends(get_feedback_repository)],
        user_service: Annotated[UserService, Depends(get_user_service)],
) -> FeedbackService:
    return FeedbackService(
        feedback_repository=feedback_repository,
        user_service=user_service,
    )

def get_deck_service(repo: Annotated[DeckRepository, Depends(get_deck_repository)]):
    return DecksService(repo)


@lru_cache
def get_s3_session() -> S3Session:
    return S3Session()

def get_s3_service(session: Annotated[S3Session, Depends(get_s3_session)]) -> S3Service:
    return S3Service(session)

def get_file_repository(session: Annotated[AsyncSession, Depends(get_session)]) -> IFileRepository:
    return FileRepository(session)

def get_file_service(
        s3_service: Annotated[S3Service, Depends(get_s3_service)],
        file_repository: Annotated[FileRepository, Depends(get_file_repository)]):
    return FileService(s3_service, file_repository)

def get_profile_service(
        file_service: Annotated[FileService, Depends(get_file_service)],
        profile_repository: Annotated[ProfileRepository, Depends(get_profile_repository)],
        user_repository: Annotated[UserRepository, Depends(get_user_repository)]):
    return ProfileService(
        file_service=file_service,
        profile_repository=profile_repository,
        user_repository=user_repository
    )

def get_auth_service(
        user_service: Annotated[UserService, Depends(get_user_service)],
        token_service: Annotated[TokenService, Depends(get_token_service)],
        profile_service: Annotated[ProfileService, Depends(get_profile_service)]):
    return AuthService(
        user_service=user_service,
        token_service=token_service,
        profile_service=profile_service
    )

def get_card_repository(session: Annotated[AsyncSession, Depends(get_session)]) -> ICardRepository:
    return CardRepository(session)


def get_card_reviews_repository(session: Annotated[AsyncSession, Depends(get_session)]) -> ICardReviewsRepository:
    return CardReviewsRepository(session)


def get_card_reviews_service(
        card_repository: Annotated[ICardRepository, Depends(get_card_repository)],
        card_reviews_repository: Annotated[ICardReviewsRepository, Depends(get_card_reviews_repository)],
        deck_repository: Annotated[IDeckRepository, Depends(get_deck_repository)],

) -> ICardReviewsService:
    return CardReviewsService(
        card_repository=card_repository,
        card_reviews_repository=card_reviews_repository,
        deck_repository=deck_repository,
    )


def get_input_builder_registry(cards_repo: Annotated[ICardRepository, Depends(get_card_repository)]) -> InputBuilderRegistry:
    registry = InputBuilderRegistry()
    registry.register(FlashCardInputBuilder.TYPE, FlashCardInputBuilder())
    registry.register(TypingInputBuilder.TYPE, TypingInputBuilder())
    registry.register(TrueFalseInputBuilder.TYPE, TrueFalseInputBuilder(cards_repo))
    registry.register(MultiChoiceInputBuilder.TYPE, MultiChoiceInputBuilder(cards_repo))
    return registry


def get_presentation_builder_registry() -> PresentationBuilderRegistry:
    registry = PresentationBuilderRegistry()
    registry.register(DefinitionPresentationBuilder.TYPE, DefinitionPresentationBuilder())
    registry.register(ImagePresentationBuilder.TYPE, ImagePresentationBuilder())
    registry.register(SoundPresentationBuilder.TYPE, SoundPresentationBuilder())
    registry.register(ClozePresentationBuilder.TYPE, ClozePresentationBuilder())
    return registry

def get_compatibility_registry() -> CompatibilityRegistry:
    registry = CompatibilityRegistry()
    registry.register_incompatible_pair(
        PresentationType.CLOZE,
        InputType.TRUE_FALSE
    )
    return registry

def get_question_builder(
        presentation_builder_registry: Annotated[PresentationBuilderRegistry, Depends(get_presentation_builder_registry)],
        input_builder_registry: Annotated[InputBuilderRegistry, Depends(get_input_builder_registry)],
        compatibility_registry: Annotated[CompatibilityRegistry, Depends(get_compatibility_registry)],
):
    return QuestionBuilder(
        presentation_builder_registry=presentation_builder_registry,
        input_builder_registry=input_builder_registry,
        compatibility_registry=compatibility_registry,
    )


def get_srs_service() -> ISrsService:
    return FsrsService()

def get_card_service(
        user_service: Annotated[UserService, Depends(get_user_service)],
        deck_service: Annotated[DecksService, Depends(get_deck_service)],
        file_service: Annotated[FileService, Depends(get_file_service)],
        card_repository: Annotated[CardRepository, Depends(get_card_repository)],
        deck_repository: Annotated[DeckRepository, Depends(get_deck_repository)],
        card_reviews_service: Annotated[CardReviewsService, Depends(get_card_reviews_service)],
        card_review_repository: Annotated[ICardReviewsRepository, Depends(get_card_reviews_repository)],
        srs_service: Annotated[ISrsService, Depends(get_srs_service)],
) -> ICardService:
    return CardService(
        user_service=user_service,
        deck_service=deck_service,
        file_service=file_service,
        card_repository=card_repository,
        deck_repository=deck_repository,
        card_reviews_service=card_reviews_service,
        card_reviews_repository=card_review_repository,
        srs_service=srs_service,
    )

def get_review_log_repository(session: Annotated[AsyncSession, Depends(get_session)]) -> IReviewLogRepository:
    return ReviewLogRepository(session=session)

def get_quiz_service(
        question_builder: Annotated[QuestionBuilder, Depends(get_question_builder)],
        deck_repository: Annotated[IDeckRepository, Depends(get_deck_repository)],
        card_service: Annotated[ICardService, Depends(get_card_service)],
        card_review_repository: Annotated[ICardReviewsRepository, Depends(get_card_reviews_repository)],
        srs_service: Annotated[ISrsService, Depends(get_srs_service)],
        review_log_repository: Annotated[IReviewLogRepository, Depends(get_review_log_repository)],
):
    return QuizService(
        question_builder=question_builder,
        deck_repository=deck_repository,
        card_service=card_service,
        card_review_repository=card_review_repository,
        srs_service=srs_service,
        review_log_repository=review_log_repository,
    )