from unittest.mock import AsyncMock, patch

import pytest
from pydantic import ValidationError

from api.v1.schemas.requests.auth_requests import ResetPasswordRequest
from api.v1.services.auth_service import AuthService
from api.v1.services.exceptions.base_exceptions import PermissionDeniedException, ValidationException
from api.v1.services.exceptions.error_codes.auth_error_codes import AuthErrorCodes
from tests.auth_service.helpers import _make_user


class TestResetPasswordSchema:
    def test_reset_password_request_success(self):
        payload = ResetPasswordRequest(
            old_password="OldPass123",
            new_password="NewPass123",
            confirmed_password="NewPass123",
        )

        assert payload.new_password == "NewPass123"

    def test_reset_password_request_passwords_must_match(self):
        with pytest.raises(ValidationError):
            ResetPasswordRequest(
                old_password="OldPass123",
                new_password="NewPass123",
                confirmed_password="OtherPass123",
            )

    def test_reset_password_request_password_strength_validation(self):
        with pytest.raises(ValidationError):
            ResetPasswordRequest(
                old_password="OldPass123",
                new_password="weak",
                confirmed_password="weak",
            )


class TestResetPasswordService:
    async def test_reset_password_success(
        self,
        auth_service: AuthService,
        user_service: AsyncMock,
        token_service: AsyncMock,
    ):
        user = _make_user(password="old_hashed")
        user_service.get_by_id.return_value = user

        with patch(
            "api.v1.services.auth_service.asyncio.to_thread",
            new_callable=AsyncMock,
            side_effect=[True, False, "new_hashed"],
        ) as mock_to_thread:
            await auth_service.reset_password(
                user_id=user.id,
                old_password="OldPass123",
                new_password="NewPass123",
            )

        assert mock_to_thread.await_count == 3
        user_service.update_password.assert_awaited_once_with(user, "new_hashed")
        token_service.deactivate_all_for_user.assert_awaited_once_with(user.id)

    async def test_reset_password_invalid_old_password(
        self,
        auth_service: AuthService,
        user_service: AsyncMock,
        token_service: AsyncMock,
    ):
        user = _make_user(password="old_hashed")
        user_service.get_by_id.return_value = user

        with patch(
            "api.v1.services.auth_service.asyncio.to_thread",
            new_callable=AsyncMock,
            return_value=False,
        ):
            with pytest.raises(PermissionDeniedException) as exc_info:
                await auth_service.reset_password(
                    user_id=user.id,
                    old_password="wrong",
                    new_password="NewPass123",
                )

        assert exc_info.value.error_code == AuthErrorCodes.INVALID_OLD_PASSWORD.value
        user_service.update_password.assert_not_awaited()
        token_service.deactivate_all_for_user.assert_not_awaited()

    async def test_reset_password_rejects_reused_password(
        self,
        auth_service: AuthService,
        user_service: AsyncMock,
        token_service: AsyncMock,
    ):
        user = _make_user(password="old_hashed")
        user_service.get_by_id.return_value = user

        with patch(
            "api.v1.services.auth_service.asyncio.to_thread",
            new_callable=AsyncMock,
            side_effect=[True, True],
        ):
            with pytest.raises(ValidationException) as exc_info:
                await auth_service.reset_password(
                    user_id=user.id,
                    old_password="OldPass123",
                    new_password="OldPass123",
                )

        assert exc_info.value.error_code == AuthErrorCodes.NEW_PASSWORD_MUST_DIFFER.value
        user_service.update_password.assert_not_awaited()
        token_service.deactivate_all_for_user.assert_not_awaited()

