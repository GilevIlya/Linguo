import io
import pytest
import uuid
from api.v1.services.schemas.file_param import FileParam

class TestUpdateProfile:
    async def test_update_profile_basic(
        self,
        profile_service,
        profile_repository,
        user_service,
        create_user,
    ):
        user = await user_service.create_user(create_user())

        await profile_service.create_profile(
            user_id=user.id,
            username="old",
            bio="old bio"
        )

        updated = await profile_service.update_profile(
            user_id=user.id,
            username="new",
            bio="new bio"
        )

        assert updated.username == "new"
        assert updated.bio == "new bio"

        db_profile = await profile_repository.get_by_user_id(user.id)
        assert db_profile.username == "new"
        assert db_profile.bio == "new bio"
    
    async def test_update_profile_only_bio(
        self,
        profile_service,
        user_service,
        create_user,
    ):
        user = await user_service.create_user(create_user())

        await profile_service.create_profile(
            user_id=user.id,
            username="username",
            bio="old bio"
        )

        updated = await profile_service.update_profile(
            user_id=user.id,
            bio="new bio"
        )

        assert updated.username == "username"
        assert updated.bio == "new bio"
    
    async def test_update_profile_with_avatar(
        self,
        profile_service,
        profile_repository,
        user_service,
        create_user,
    ):
        user = await user_service.create_user(create_user())
        username = f"user_{uuid.uuid4().hex[:8]}"

        await profile_service.create_profile(
            user_id=user.id,
            username=username
        )

        file = FileParam(
            content=io.BytesIO(b"image"),
            content_type="image/png",
            size=100
        )

        updated = await profile_service.update_profile(
            user_id=user.id,
            avatar=file
        )

        assert updated.avatar_file_key is not None

        db_profile = await profile_repository.get_by_user_id(user.id)
        assert db_profile.avatar_file_key is not None

    async def test_update_profile_replace_avatar(
        self,
        profile_service,
        user_service,
        create_user,
    ):
        user = await user_service.create_user(create_user())
        username = f"user_{uuid.uuid4().hex[:8]}"

        await profile_service.create_profile(
            user_id=user.id,
            username=username
        )

        file1 = FileParam(
            content=io.BytesIO(b"img1"),
            content_type="image/png",
            size=100
        )

        file2 = FileParam(
            content=io.BytesIO(b"img2"),
            content_type="image/png",
            size=100
        )

        first = await profile_service.update_profile(
            user_id=user.id,
            avatar=file1
        )

        second = await profile_service.update_profile(
            user_id=user.id,
            avatar=file2
        )

        assert first.avatar_file_key != second.avatar_file_key

    async def test_update_profile_not_found(self, profile_service):
        with pytest.raises(Exception):
            await profile_service.update_profile(
                user_id=uuid.uuid4(),
                username="test"
            )