from datetime import timedelta

from pydantic_settings import BaseSettings


class SrsConfig(BaseSettings):
    DESIRED_RETENTION: float = 0.9
    LEARNING_STEPS: tuple[timedelta, ...] = (
            timedelta(minutes=1),
            timedelta(minutes=10),
        )
    RELEARNING_STEPS: tuple[timedelta, ...] = (
        timedelta(minutes=10),
    )
    MAX_INTERVAL: int = 365
    FUZZING: bool = True

srs_config = SrsConfig()
