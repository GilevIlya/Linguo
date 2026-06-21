import hashlib
from unittest.mock import AsyncMock

import pytest

from api.v1.models import User
from api.v1.repositories.token_repository import TokenRepository
from api.v1.repositories.user_repository import UserRepository
from api.v1.services.auth_service import AuthService
from api.v1.services.exceptions.base_exceptions import AuthException, PermissionDeniedException, ValidationException
from api.v1.services.exceptions.error_codes.auth_error_codes import AuthErrorCodes
from api.v1.services.profile_service import ProfileService
from api.v1.services.tokens_service import TokenService
from api.v1.services.user_service import UserService
from api.v1.services.utils.hash import hash_password


@pytest.fixture
async def auth_service_integration(session):
    user_repo = UserRepository(session)
    token_repo = TokenRepository(session)
    profile_service = AsyncMock(spec=ProfileService)

    return AuthService(
        user_service=UserService(user_repo),
        token_service=TokenService(token_repo),
        profile_service=profile_service,
    )


class TestResetPasswordIntegration:
    async def test_reset_password_changes_credentials_and_invalidates_refresh_tokens(
        self, auth_service_integration: AuthService
    ):
        old_password = "OldPass123"
        new_password = "NewPass123"
        user = User(email="reset_pwd_success@test.com", password=hash_password(old_password))
        await auth_service_integration.user_service.create_user(user)

        issued_tokens = await auth_service_integration.login(user.email, old_password)

        await auth_service_integration.reset_password(
            user_id=user.id,
            old_password=old_password,
            new_password=new_password,
        )

        with pytest.raises(AuthException) as old_login_error:
            await auth_service_integration.login(user.email, old_password)

        assert old_login_error.value.error_code == AuthErrorCodes.EMAIL_OR_PASSWORD_INCORRECT.value

        new_login_tokens = await auth_service_integration.login(user.email, new_password)
        assert new_login_tokens.access_token

        hashed_refresh = hashlib.sha256(issued_tokens.refresh_token.token.encode()).hexdigest()
        token_entity = await auth_service_integration.token_service.token_repository.get_by_token(hashed_refresh)
        assert token_entity is None

    async def test_reset_password_invalid_old_password(
        self, auth_service_integration: AuthService
    ):
        user = User(email="reset_pwd_invalid_old@test.com", password=hash_password("OldPass123"))
        await auth_service_integration.user_service.create_user(user)

        with pytest.raises(PermissionDeniedException) as exc_info:
            await auth_service_integration.reset_password(
                user_id=user.id,
                old_password="WrongPass123",
                new_password="NewPass123",
            )

        assert exc_info.value.error_code == AuthErrorCodes.INVALID_OLD_PASSWORD.value

    async def test_reset_password_rejects_reused_password(
        self, auth_service_integration: AuthService
    ):
        password = "SamePass123"
        user = User(email="reset_pwd_reuse@test.com", password=hash_password(password))
        await auth_service_integration.user_service.create_user(user)

        with pytest.raises(ValidationException) as exc_info:
            await auth_service_integration.reset_password(
                user_id=user.id,
                old_password=password,
                new_password=password,
            )

        assert exc_info.value.error_code == AuthErrorCodes.NEW_PASSWORD_MUST_DIFFER.value

