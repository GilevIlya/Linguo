from api.v1.models import Card
from api.v1.models.types.additional_fields import AdditionalFieldType


def extract_additional_field(card: Card, field_type: AdditionalFieldType) -> str | None:
    for i in card.additional_fields:
        if i.type == field_type:
            return i.content
    return None
