import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta
from logging import getLogger
from uuid import UUID

from api.v1.configs.security_config import security_config
from api.v1.models import User
from api.v1.services.exceptions.base_exceptions import (
    AuthException,
    NotFoundException,
    PermissionDeniedException,
    ValidationException,
)
from api.v1.services.exceptions.error_codes.auth_error_codes import AuthErrorCodes
from api.v1.services.profile_service import ProfileService
from api.v1.services.tokens_service import RefreshToken, TokenService
from api.v1.services.user_service import UserService
from api.v1.services.utils.hash import hash_password, check_password
from api.v1.services.utils.jwt import JWTPayload, sign_jwt

logger = getLogger("app")


@dataclass(frozen=True)
class TokensPair:
    access_token: str
    refresh_token: RefreshToken


class AuthService:
    _ACCESS_TOKEN_TTL_SEC = security_config.ACCESS_TOKEN_EXPIRE_SEC

    def __init__(self, user_service: UserService, token_service: TokenService, profile_service: ProfileService):
        self.token_service = token_service
        self.user_service = user_service
        self.profile_service = profile_service

    async def register(self, username: str, email: str, password: str) -> TokensPair:
        # TODO: проверку на то что пароль нормальный и анотацию добавить
        hashed = await asyncio.to_thread(hash_password, password)
        user = User(
            email=email,
            password=hashed,
        )
        await self.user_service.create_user(user)
        await self.profile_service.create_profile(
            user_id=user.id,
            username=username,
        )
        token = await self.token_service.create_token(user.id)
        logger.info("User registered: id=%s", user.id)

        return TokensPair(
            access_token=self._build_access_token(user.id),
            refresh_token=token,
        )

    async def login(self, email: str, password: str) -> TokensPair:
        """Authenticate user and return a token pair."""
        try:
            user = await self.user_service.get_by_email(email)
        except NotFoundException:
            logger.warning("Login failed: user not found for email=%s", email)
            raise AuthException(
                error_code=AuthErrorCodes.EMAIL_OR_PASSWORD_INCORRECT.value,
                message="Email or password is incorrect",
            )

        password_valid = await asyncio.to_thread(check_password, password, user.password)
        if not password_valid:
            logger.warning("Login failed: wrong password for email=%s", email)
            raise AuthException(
                error_code=AuthErrorCodes.EMAIL_OR_PASSWORD_INCORRECT.value,
                message="Email or password is incorrect",
            )

        token = await self.token_service.create_token(user.id)
        logger.info("User logged in: id=%s", user.id)

        return TokensPair(
            access_token=self._build_access_token(user.id),
            refresh_token=token,
        )

    async def logout(self, refresh_token: str) -> None:
        """Invalidate the given refresh token."""
        deactivated = await self.token_service.deactivate_token(refresh_token)
        if not deactivated:
            logger.warning("Logout: token not found or already expired")

    async def refresh(self, refresh_token: str) -> TokensPair:
        """
        Performs refresh token rotation and returns a new token pair.

        Consumes the provided refresh token in a single DB query via rotate().
        If the token is invalid or expired, raises AuthException.
        Issues a new refresh token and a new access token for the same user.

        Args:
            refresh_token (str): The current raw refresh token from the client cookie.

        Returns:
            TokensPair: A new pair of access and refresh tokens.

        Raises:
            AuthException: If the refresh token is invalid, expired, or not found.
        """
        token_entity = await self.token_service.rotate(refresh_token)
        if not token_entity:
            logger.warning("Refresh failed: token is invalid, expired or not found")
            raise AuthException(
                error_code=AuthErrorCodes.INVALID_OR_EXPIRED_REFRESH_TOKEN.value,
                message="Refresh token is invalid or expired",
            )

        user_id = token_entity.user_id
        new_token = await self.token_service.create_token(user_id)
        logger.info("Token refreshed: user_id=%s", user_id)

        return TokensPair(
            access_token=self._build_access_token(user_id),
            refresh_token=new_token,
        )

    async def reset_password(self, user_id: UUID, old_password: str, new_password: str) -> None:
        user = await self.user_service.get_by_id(user_id)

        is_old_password_valid = await asyncio.to_thread(check_password, old_password, user.password)
        if not is_old_password_valid:
            logger.warning("Reset password failed: invalid old password for user_id=%s", user_id)
            raise PermissionDeniedException(
                error_code=AuthErrorCodes.INVALID_OLD_PASSWORD.value,
                message="Old password is incorrect",
            )

        is_password_reused = await asyncio.to_thread(check_password, new_password, user.password)
        if is_password_reused:
            logger.warning("Reset password failed: new password equals old password for user_id=%s", user_id)
            raise ValidationException(
                error_code=AuthErrorCodes.NEW_PASSWORD_MUST_DIFFER.value,
                message="New password must be different from old password",
            )

        hashed_password = await asyncio.to_thread(hash_password, new_password)
        await self.user_service.update_password(user, hashed_password)
        deactivated_count = await self.token_service.deactivate_all_for_user(user.id)

        logger.info(
            "Password reset succeeded: user_id=%s, deactivated_refresh_tokens=%d",
            user_id,
            deactivated_count,
        )

    def _build_access_token(self, user_id: UUID) -> str:
        payload = JWTPayload(
            sub=str(user_id),
            exp=datetime.now() + timedelta(seconds=self._ACCESS_TOKEN_TTL_SEC),
        )
        return sign_jwt(payload)
