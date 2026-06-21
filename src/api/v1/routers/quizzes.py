from uuid import UUID

from fastapi import APIRouter, Depends
from starlette import status

from api.v1.routers.security import get_current_user_id
from api.v1.routers.utils.dependencies import get_quiz_service
from api.v1.schemas.requests.quiz_requests import RatingRequest
from api.v1.schemas.responses.base_response import BaseMessageResponse
from api.v1.schemas.responses.quizzes import Question, NextQuestion, PresentationContext, InputContext, InputContent
from api.v1.services.quiz_service import QuizService
from api.v1.services.schemas.quizzes import InputTypeDTO, PresentationTypeDTO

router = APIRouter(
    prefix="/quizzes",
    tags=["quizzes"],
)

@router.get(
    path="/get-next-question",
    summary="Get next question for deck",
    description="takes out the most expired card from the users deck and builds a quiz question from it",
    response_model=NextQuestion,
    status_code=status.HTTP_200_OK,
)
async def quizzes(
        deck_id: UUID,
        # excluded_inputs: list[InputTypeDTO] | None = Query(None),
        # excluded_presentations: list[PresentationTypeDTO] | None = Query(None), #TODO:/ придумать
        actor_id: UUID = Depends(get_current_user_id),

        quiz_service: QuizService = Depends(get_quiz_service)
) -> NextQuestion:
    question, review_id = await quiz_service.get_next_question_by_deck(
        actor_id=actor_id,
        deck_id=deck_id,
        excepted_inputs=[],
        excepted_presentations=[],
        # excepted_inputs=excluded_inputs or [],
        # excepted_presentations=excluded_presentations or [],
    )
    return NextQuestion(
        review_id=review_id,
        question=Question(
            presentation=PresentationContext(
                type=PresentationTypeDTO(question.presentation.type),
                content=question.presentation.content,
            ),
            input=InputContext(
                correct_answer=question.input.correct_answer,
                content=InputContent(
                    type=InputTypeDTO(question.input.type),
                    content=question.input.content.to_dict(),
                )
            )
        )
    )

@router.patch(
    path="/rate-question",
    summary="Rate question after review",
    description="Giving the user's answer after we have received the answer in get-next-question",
    response_model=BaseMessageResponse,
    status_code=status.HTTP_200_OK,
)
async def rate_question(rating_req: RatingRequest, actor_id: UUID = Depends(get_current_user_id), quiz_service: QuizService = Depends(get_quiz_service)):
    await quiz_service.rate_question(
        actor_id=actor_id,
        review_card_id=rating_req.review_id,
        current_datetime=rating_req.review_date_time,
        rating=rating_req.rating,
        review_duration=rating_req.review_duration,
    )
    return BaseMessageResponse(message="Rating submitted successfully, please get next question")
