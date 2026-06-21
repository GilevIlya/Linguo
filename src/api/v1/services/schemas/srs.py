from dataclasses import dataclass

from api.v1.models import CardReview, ReviewLog


@dataclass
class ReviewResult:
    card_review: CardReview
    review_log: ReviewLog
