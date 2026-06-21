from typing import Any

from pydantic import BaseModel


class SimilarRequest(BaseModel):
    arr: list[str]
    topn: int = 10


class WordLevelRequest(BaseModel):
    word: str
    translation: str


class SentenceRequest(BaseModel):
    word: str
    level: str
    language: str


class UserSentenceRequest(BaseModel):
    user_sentence: str


class SentenceContextRequest(BaseModel):
    word: str
    user_sentence: str


class PredictRequest(BaseModel):
    features: dict[str, Any]


class PredictTopicRequest(BaseModel):
    sentence: str


class PredictTopicsRequest(BaseModel):
    sentences: list[str]


class CheckPlagiarismRequest(BaseModel):
    user_text: str
    get_index: bool = False


class SpamClassificationRequest(BaseModel):
    user_sentence: str


class PreprocessRequest(BaseModel):
    sentence: str
    language: str