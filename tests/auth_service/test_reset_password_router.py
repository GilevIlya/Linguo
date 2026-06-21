from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from api.v1.routers.security import get_current_user_id
from api.v1.routers.utils.dependencies import get_auth_service
from api.v1.services.exceptions.base_exceptions import PermissionDeniedException, ValidationException
from api.v1.services.exceptions.error_codes.auth_error_codes import AuthErrorCodes
from src.main import get_app


@pytest.fixture
def client_and_auth_mock():
    app = get_app()
    auth_service_mock = AsyncMock()
    user_id = uuid4()

    app.dependency_overrides[get_auth_service] = lambda: auth_service_mock
    app.dependency_overrides[get_current_user_id] = lambda: user_id

    with TestClient(app) as client:
        yield client, auth_service_mock, user_id

    app.dependency_overrides.clear()


class TestResetPasswordRouter:
    def test_reset_password_success(self, client_and_auth_mock):
        client, auth_service_mock, user_id = client_and_auth_mock

        response = client.post(
            "/api/v1/auth/reset-password",
            json={
                "old_password": "OldPass123",
                "new_password": "NewPass123",
                "confirmed_password": "NewPass123",
            },
        )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["message"] == "Password has been reset successfully"
        auth_service_mock.reset_password.assert_awaited_once_with(
            user_id=user_id,
            old_password="OldPass123",
            new_password="NewPass123",
        )

    def test_reset_password_validation_error(self, client_and_auth_mock):
        client, _, _ = client_and_auth_mock

        response = client.post(
            "/api/v1/auth/reset-password",
            json={
                "old_password": "OldPass123",
                "new_password": "weak",
                "confirmed_password": "weak",
            },
        )

        assert response.status_code == 422

    def test_reset_password_invalid_old_password_returns_403(self, client_and_auth_mock):
        client, auth_service_mock, _ = client_and_auth_mock
        auth_service_mock.reset_password.side_effect = PermissionDeniedException(
            error_code=AuthErrorCodes.INVALID_OLD_PASSWORD.value,
            message="Old password is incorrect",
        )

        response = client.post(
            "/api/v1/auth/reset-password",
            json={
                "old_password": "WrongPass123",
                "new_password": "NewPass123",
                "confirmed_password": "NewPass123",
            },
        )

        assert response.status_code == 403
        assert response.json()["error"]["code"] == AuthErrorCodes.INVALID_OLD_PASSWORD.value

    def test_reset_password_reused_password_returns_400(self, client_and_auth_mock):
        client, auth_service_mock, _ = client_and_auth_mock
        auth_service_mock.reset_password.side_effect = ValidationException(
            error_code=AuthErrorCodes.NEW_PASSWORD_MUST_DIFFER.value,
            message="New password must be different from old password",
        )

        response = client.post(
            "/api/v1/auth/reset-password",
            json={
                "old_password": "OldPass123",
                "new_password": "OldPass123",
                "confirmed_password": "OldPass123",
            },
        )

        assert response.status_code == 400
        assert response.json()["error"]["code"] == AuthErrorCodes.NEW_PASSWORD_MUST_DIFFER.value

    def test_reset_password_without_auth_returns_error(self):
        app = get_app()
        app.dependency_overrides[get_auth_service] = lambda: AsyncMock()

        with TestClient(app) as client:
            response = client.post(
                "/api/v1/auth/reset-password",
                json={
                    "old_password": "OldPass123",
                    "new_password": "NewPass123",
                    "confirmed_password": "NewPass123",
                },
            )

        app.dependency_overrides.clear()
        assert response.status_code in {401, 403}

