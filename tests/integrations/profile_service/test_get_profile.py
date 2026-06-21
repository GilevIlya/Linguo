import pytest


@pytest.mark.asyncio
async def test_get_profile(
    profile_service,
    user_service,
    create_user,
):
    user = await user_service.create_user(create_user())

    await profile_service.create_profile(
        user_id=user.id,
        username="test",
        bio="bio"
    )

    profile = await profile_service.get_profile(user.id)

    assert profile.username == "test"
    assert profile.bio == "bio"

@pytest.mark.asyncio
async def test_get_profile_not_found(profile_service):
    import uuid
    with pytest.raises(Exception):
        await profile_service.get_profile(uuid.uuid4())