import pytest
import uuid


@pytest.mark.asyncio
async def test_create_profile(
    profile_service,
    user_service,
    create_user,
    profile_repository,
):
    user = await user_service.create_user(create_user())
    username = f"user_{uuid.uuid4().hex[:6]}"
    bio = "test bio"

    profile = await profile_service.create_profile(
        user_id=user.id,
        username=username,
        bio=bio
    )

    assert profile.id is not None
    assert profile.user_id == user.id
    assert profile.username == username
    assert profile.bio == bio

    db_profile = await profile_repository.get_by_user_id(user.id)

    assert db_profile is not None
    assert db_profile.username == username
    assert db_profile.bio == bio