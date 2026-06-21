from pydantic import BaseModel
from api.v1.schemas.responses.base_response import BaseMessageResponse

from uuid import UUID

class ProfileSimpleView(BaseModel):
    profile_id: UUID
    username: str
    bio: str | None
    avatar_file_key: str | None

class ProfileUpdatingResponse(BaseMessageResponse[ProfileSimpleView]):
    """Response schema for successful profile updating."""
    message: str = "Profile updated successfully"

class ProfileGettingResponse(BaseMessageResponse[ProfileSimpleView]):
    """Response schema for successful profile getting"""
    message: str = "Profile recieved successfully"