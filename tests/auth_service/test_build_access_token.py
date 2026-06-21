import uuid
from datetime import datetime, timedelta
from unittest.mock import patch

from api.v1.configs.security_config import security_config
from api.v1.services.utils.jwt import JWTPayload


class TestBuildAccessToken:
    def test_access_token_payload_contains_user_id(self, auth_service):
        uid = uuid.uuid4()
        with patch("api.v1.services.auth_service.sign_jwt") as mock_sign:
            auth_service._build_access_token(uid)

        payload = mock_sign.call_args[0][0]
        assert isinstance(payload, JWTPayload)
        assert payload.sub == str(uid)

    def test_access_token_expiry(self, auth_service):
        uid = uuid.uuid4()
        before = datetime.now()
        with patch("api.v1.services.auth_service.sign_jwt") as mock_sign:
            auth_service._build_access_token(uid)

        payload = mock_sign.call_args[0][0]
        max_expected = before + timedelta(seconds=security_config.ACCESS_TOKEN_EXPIRE_SEC + 5)
        assert payload.exp <= max_expected
