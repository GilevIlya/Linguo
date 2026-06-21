import pytest
from api.v1.services.user_service import UserService
from api.v1.services.exceptions.base_exceptions import AlreadyExistsException

async def test_create_user(user_service: UserService, create_user):
    user = create_user()
    created_user = await user_service.create_user(user)
    assert created_user.id == user.id
    assert created_user.email == user.email

async def test_create_user_with_existing_email(user_service: UserService, create_user):
    user1 = create_user()
    user2 = create_user()
    user1.email = user2.email 

    await user_service.create_user(user1)

    with pytest.raises(AlreadyExistsException) as exc_info:
        await user_service.create_user(user2)
    
    assert exc_info.value.error_code == "EMAIL_ALREADY_IN_USE"