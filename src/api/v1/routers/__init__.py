from fastapi import APIRouter

from .auth import router as auth_router
from .cards_routers import cards_router
from .decks import decks_router
from .feedbacks import feedback_router
from .files_routers import files_router
from .profiles import profile_router
from .ml_routers import ml_router
from .quizzes import router as quizzes_router

router = APIRouter(prefix="/api/v1")

router.include_router(auth_router)
router.include_router(decks_router)
router.include_router(cards_router)
router.include_router(files_router)
router.include_router(profile_router)
router.include_router(quizzes_router)
router.include_router(files_router)
router.include_router(ml_router)
router.include_router(feedback_router)
