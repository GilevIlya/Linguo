from api.v1.configs.ml_config import get_ml_config
from api.v1.services.interfaces.ExternalApiService import ExternalAPIService

from typing import Any

from api.v1.schemas.requests.ml_requests import (
    SimilarRequest,
    WordLevelRequest,
    SentenceRequest,
    PredictRequest,
    PredictTopicRequest,
    PredictTopicsRequest,
    PreprocessRequest,
    CheckPlagiarismRequest,
    SpamClassificationRequest,
    UserSentenceRequest,
    SentenceContextRequest,
)


class MLService(ExternalAPIService):
    def __init__(self) -> None:
        super().__init__(get_ml_config())

    async def test_service(self) -> dict[str, Any] | None:
        return await self.get("/posts")
    

    async def recieve_similar_words(
        self,
        data: SimilarRequest,
    ) -> dict[str, Any] | None:
        return await self.post("/similar", body=data.model_dump())

    async def get_word_level(
        self,
        data: WordLevelRequest,
    ) -> dict[str, Any] | None:
        return await self.post("/word_level", body=data.model_dump())

    async def generate_sentence(
        self,
        data: SentenceRequest,
    ) -> dict[str, Any] | None:
        return await self.post("/sentence", body=data.model_dump())

    async def correct_paragraph(
        self,
        data: UserSentenceRequest,
    ) -> dict[str, Any] | None:
        return await self.post("/correct_paragraph", body=data.model_dump())

    async def get_sentence_level(
        self,
        data: UserSentenceRequest,
    ) -> dict[str, Any] | None:
        return await self.post("/sentence_level", body=data.model_dump())

    async def get_sentence_context_level(
        self,
        data: SentenceContextRequest,
    ) -> dict[str, Any] | None:
        return await self.post("/sentence_context_level", body=data.model_dump())

    async def rate_sentence_context(
        self,
        data: SentenceContextRequest,
    ) -> dict[str, Any] | None:
        return await self.post("/sentence_context_rate", body=data.model_dump())

    async def predict_level(
        self,
        data: PredictRequest,
    ) -> dict[str, Any] | None:
        return await self.post("/predict", body=data.model_dump())

    async def predict_topic(
        self,
        data: PredictTopicRequest,
    ) -> dict[str, Any] | None:
        return await self.post("/predict_topic", body=data.model_dump())

    async def predict_topics(
        self,
        data: PredictTopicsRequest,
    ) -> dict[str, Any] | None:
        return await self.post("/predict_topics", body=data.model_dump())

    async def check_plagiarism(
        self,
        data: CheckPlagiarismRequest,
    ) -> dict[str, Any] | None:
        return await self.post("/check_plagiarism", body=data.model_dump())

    async def classify_spam(
        self,
        data: SpamClassificationRequest,
    ) -> dict[str, Any] | None:
        return await self.post("/spam_classification", body=data.model_dump())

    async def preprocess_text(
        self,
        data: PreprocessRequest,
    ) -> dict[str, Any] | None:
        return await self.post("/preprocess", body=data.model_dump())
    
