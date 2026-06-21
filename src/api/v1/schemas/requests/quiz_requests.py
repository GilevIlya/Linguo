from datetime import datetime, timezone
from enum import IntEnum
from uuid import UUID

from pydantic import BaseModel, AwareDatetime, field_validator


class Rating(IntEnum):
    """
    AGAIN == Не знаю | Don't know: 1
    HARD == Знаю с трудом | I hardly know: 2
    GOOD == Знаю | I know.: 3

    """
    AGAIN = 1
    HARD = 2
    GOOD = 3


class RatingRequest(BaseModel):
    """
    review_id: UUID: The uuid that was retrieved in /get-next-question
    rating: Rating: The rating that was given during the answer
    review_date_time: datetime: The date and time the rating was given. Must be in UTC.
    review_duration: int: Time in which the user gave an answer in milliseconds
    """
    review_id: UUID
    rating: Rating
    review_date_time: AwareDatetime
    review_duration: int


    @field_validator("review_date_time", mode="after")
    @classmethod
    def to_utc(cls, v: datetime) -> datetime:
        return v.astimezone(timezone.utc)