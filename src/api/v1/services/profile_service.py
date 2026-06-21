from typing import Any
from uuid import UUID

from sqlalchemy.exc import IntegrityError

from api.v1.models.profiles import Profile
from api.v1.repositories.profile_repository import ProfileRepository
from api.v1.repositories.user_repository import UserRepository
from api.v1.services.exceptions.base_exceptions import AlreadyExistsException
from api.v1.services.exceptions.base_exceptions import NotFoundException, BusinessLogicException
from api.v1.services.exceptions.error_codes.profiles_error_codes import ProfilesErrorCodes
from api.v1.services.file_service import FileService
from .schemas.file_param import FileParam
from .schemas.file_prefix import FilePrefix
from ..schemas.responses.profile import ProfileSimpleView


class ProfileService:
    USERNAME_MAX_LENGTH = 54
    USERNAME_MIN_LENGTH = 3
    BIO_MAX_LENGTH = 300 # TODO :/ вынести всю эту хуйню куда то она мне тут воняет

    def __init__(
        self,
        file_service: FileService,
        profile_repository: ProfileRepository,
        user_repository: UserRepository
    ):
        self.file_service = file_service
        self.profile_repository = profile_repository
        self.user_repository = user_repository
    
    async def create_profile(
        self,
        user_id: UUID,
        username: str,
        bio: str | None = None,
        avatar_file_key: str | None = None
    ) -> Profile:
        self._validate_bio(bio or "")
        profile = Profile(
            user_id=user_id,
            username=username.strip(),
            bio=bio,
            avatar_file_key=avatar_file_key
        )
        self._validate_username(profile.username)
        try:
            profile = await self.profile_repository.create(profile)
            return profile
        except IntegrityError:
            raise AlreadyExistsException(
                error_code=ProfilesErrorCodes.USERNAME_ALREADY_IN_USE.value,
                message="User already has a profile"
            )
    
    async def update_profile(
        self,
        user_id: UUID,
        username: str | None = None,
        bio: str | None = None,
        avatar: FileParam | None = None,
    ) -> ProfileSimpleView:
        profile = await self._get_profile_entity(user_id)

        update_data: dict[str, Any] = {}

        if username is not None and username != profile.username:
            self._validate_username(username)
            update_data["username"] = username.strip()

        if bio is not None and bio != profile.bio:
            self._validate_bio(bio)
            update_data["bio"] = bio

        if avatar is not None:
            new_avatar_key = await self.file_service.upload_file(
                prefix=FilePrefix.AVATARS,
                file=avatar,
                owner_id=user_id,
            )
            old_avatar_key = profile.avatar_file_key
            update_data["avatar_file_key"] = new_avatar_key

        try:
            updated_profile = await self.profile_repository.update(profile, update_data)
        except IntegrityError:
            raise AlreadyExistsException(
                error_code=ProfilesErrorCodes.USERNAME_ALREADY_IN_USE.value,
                message="Username is already in use"
            )

        if avatar is not None and old_avatar_key is not None:
            await self.file_service.delete_file(old_avatar_key, owner_id=user_id)

        return ProfileSimpleView(
            profile_id=updated_profile.id,
            username=updated_profile.username,
            bio=updated_profile.bio,
            avatar_file_key=updated_profile.avatar_file_key
        )

    async def get_profile(
        self,
        user_id: UUID
    ) -> ProfileSimpleView:
        profile = await self._get_profile_entity(user_id)
        return ProfileSimpleView(
            profile_id=profile.id,
            username=profile.username,
            bio=profile.bio,
            avatar_file_key=profile.avatar_file_key
        )


    async def _get_profile_entity(
        self,
        user_id: UUID
    ) -> Profile:
        profile = await self.profile_repository.get_by_user_id(user_id)
        if not profile:
            raise NotFoundException(
                error_code=ProfilesErrorCodes.PROFILE_NOT_FOUND.value,
                message="Profile for user not found",
            )
        return profile

    def _validate_username(self, username: str) -> None:
        username = username.strip() if username else ""
        if not username or len(username) < self.USERNAME_MIN_LENGTH or len(username) > self.USERNAME_MAX_LENGTH:
            raise BusinessLogicException(
                error_code=ProfilesErrorCodes.USERNAME_MUST_BE_BETWEEN_3_AND_50_CHARACTERS.value,
                message="Username must be between 3 and 50 characters long"
            )

    def _validate_bio(self, bio: str) -> None:
        bio = bio.strip() if bio else ""
        if len(bio) > self.BIO_MAX_LENGTH:
            raise BusinessLogicException(
                error_code=ProfilesErrorCodes.BIO_MUST_BE_AT_MOST_300_CHARACTERS.value,
                message="Bio must be at most 300 characters long"
            )
