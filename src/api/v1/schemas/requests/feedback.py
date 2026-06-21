from enum import StrEnum

from pydantic import BaseModel, Field


class FeedbackTypeDto(StrEnum):
    """Enumeration of supported feedback categories.

    Attributes:
        BUG: Indicates a bug report or technical issue.
        WISH: Indicates a feature request or suggestion.
        OTHER: Indicates feedback that does not fall into the other categories.
    """
    BUG = "BUG"
    WISH = "WISH"
    OTHER = "OTHER"


class CreateFeedbackRequest(BaseModel):
    """Request DTO for creating new user feedback.

    This model validates and structures incoming feedback data from clients,
    ensuring the message length, feedback type, and timing information meet
    the API's requirements.

    Attributes:
        message: The textual content of the user's feedback. Maximum 550 characters.
        feedback_type: The category of feedback being submitted (bug, wish, or other).
        form_filled_time_ms: The time taken by the user to fill out the feedback form
            in milliseconds. Must be greater than 1.

    Example:
        >>> request = CreateFeedbackRequest(
        ...     message="The checkout process was seamless and fast!",
        ...     feedback_type=FeedbackTypeDto.WISH,
        ...     form_filled_time_ms=1500
        ... )
    """
    message: str = Field(
        min_length=1,
        max_length=550,
        description="The textual content of the user's feedback. Maximum 550 characters.",
        examples=["The checkout process was seamless and fast!"]
    )
    feedback_type: FeedbackTypeDto
    form_filled_time_ms: int = Field(
        gt=1,
        description="Time taken to fill the form in milliseconds. Must be greater than 1."
    )
