import pytest

from api.v1.repositories.profile_repository import ProfileRepository
from api.v1.services.profile_service import ProfileService

@pytest.fixture()
async def profile_repository(session):
    return ProfileRepository(session)

@pytest.fixture()
async def profile_service(file_service, profile_repository, user_repository):
    return ProfileService(
        file_service=file_service,
        profile_repository=profile_repository,
        user_repository=user_repository
    )