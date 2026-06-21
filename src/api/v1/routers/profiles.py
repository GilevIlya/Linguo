from fastapi import APIRouter, Depends, Form, UploadFile
from typing import Annotated
from uuid import UUID

from .utils.dependencies import get_profile_service
from .security import get_current_user_id

from api.v1.services.profile_service import ProfileService
from api.v1.services.schemas.file_param import FileParam
from api.v1.schemas.responses.profile import ProfileUpdatingResponse, ProfileGettingResponse

profile_router = APIRouter(
    prefix="/profiles",
    tags=['profiles']
)


@profile_router.patch(
    path="/",
    summary="Profile update",
    response_model=ProfileUpdatingResponse,

    description="""Update the current user's profile fields.
        All fields are optional — only provided fields will be updated.
        - **username**: new display name
        - **bio**: short text about the user
        - **avatar**: image file (JPEG/PNG); replaces the existing avatar if present
        """,
)
async def update_profile(
    username: Annotated[str | None, Form()] = None,
    bio: Annotated[str | None, Form()] = None,
    avatar: UploadFile | None = None,
    user_id: UUID = Depends(get_current_user_id),
    profile_service: ProfileService = Depends(get_profile_service)
) -> ProfileUpdatingResponse:
    avatar_param: FileParam | None = None
    if avatar:
        avatar_param = FileParam(content=avatar.file, content_type=avatar.content_type, original_name=avatar.filename, size=avatar.size)
    updated_profile = await profile_service.update_profile(
        user_id=user_id,
        username=username,
        bio=bio,
        avatar=avatar_param,
    )
    return ProfileUpdatingResponse(
        data=updated_profile
    )

@profile_router.get(
    path="/me",
    summary="Get user profile info",
    response_model=ProfileGettingResponse,

    description="""Return the profile of the currently authenticated user.""",
)
async def get_profile(
    user_id: UUID = Depends(get_current_user_id),
    profile_service: ProfileService = Depends(get_profile_service)
) -> ProfileGettingResponse:
    profile = await profile_service.get_profile(user_id=user_id)
    return ProfileGettingResponse(
        data=profile
    )