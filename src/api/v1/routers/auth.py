from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, Response

from api.v1.schemas.requests.auth_requests import (
    AuthenticationRequest,
    RegistrationRequest,
    ResetPasswordRequest,
)
from api.v1.schemas.responses.auth import (
    AuthenticationResponse,
    AccessTokenResponse,
    ResetPasswordResponse,
)
from api.v1.services.auth_service import AuthService
from .security import get_current_user_id
from .utils.dependencies import get_auth_service
from ..configs.security_config import security_config
from ..schemas.responses import ErrorResponse

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

REFRESH_TOKEN_COOKIE_PATH = "/api/v1/auth"


def _set_refresh_token_cookie(response: Response, refresh_token: str):
    response.set_cookie(
        key=security_config.COOKIE_NAME_REFRESH_TOKEN,
        value=refresh_token,
        httponly=True,
        secure=True,
        path=REFRESH_TOKEN_COOKIE_PATH,
        max_age=security_config.REFRESH_TOKEN_EXPIRE_SEC,
    )


def _clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(key=security_config.COOKIE_NAME_REFRESH_TOKEN, path=REFRESH_TOKEN_COOKIE_PATH)


@router.get(
    path="/ping",
    responses={
        401: {
            "description": "Not authenticated",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "error": {
                            "code": "HTTP_401",
                            "message": "Not authenticated",
                            "details": None
                        },
                        "time": "2026-02-20T15:30:54.651976"
                    }
                }
            }
        },
        403: {
            "description": "Jwt is invalid or expired",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "error": {
                            "code": "FORBIDDEN",
                            "message": "Jwt is invalid or expired",
                            "details": None
                        },
                        "time": "2026-02-20T15:31:33.809360"
                    }
                }
            }
        }
    })
async def ping(user_id: UUID = Depends(get_current_user_id)) -> dict:
    return {"message": "protected pong", "user_id": user_id}


@router.post(
    path="/login",
    summary="User login",
    description=(
            "Authenticate a user with email and password. "
            "Returns an access token in the response body and sets a httpOnly refresh token cookie."
    ),
    response_model=AuthenticationResponse,
    responses={
        200: {"description": "Authentication successful"},
        401: {"description": "Invalid email or password"},
    },
)
async def login(
        res: Response,
        data: AuthenticationRequest,
        service: AuthService = Depends(get_auth_service),
) -> AuthenticationResponse:
    tokens = await service.login(email=data.email, password=data.password)
    _set_refresh_token_cookie(res, tokens.refresh_token.token)
    return AuthenticationResponse(
        data=AccessTokenResponse(access_token=tokens.access_token)
    )


@router.post(
    path="/logout",
    summary="User logout",
    description=(
            "Invalidates the refresh token stored in the httpOnly cookie and clears it. "
            "Returns 204 No Content regardless of whether the cookie was present."
    ),
    status_code=204,
    response_model=None,
    responses={
        204: {"description": "Successfully logged out"},
    },
)
async def logout(
        req: Request,
        res: Response,
        service: AuthService = Depends(get_auth_service),
) -> None:
    refresh_token = req.cookies.get(security_config.COOKIE_NAME_REFRESH_TOKEN)
    if refresh_token:
        await service.logout(refresh_token)
    _clear_refresh_cookie(res)


@router.post(
    path="/refresh",
    summary="Refresh token rotation",
    description=(
            "Rotates the refresh token: invalidates the current one, issues a new refresh token "
            "(set as httpOnly cookie) and returns a new access token in the response body. "
            "Requires a valid refresh token cookie."
    ),
    response_model=AuthenticationResponse,
    responses={
        200: {"description": "Tokens successfully refreshed"},
        401: {"description": "Refresh token is missing, invalid or expired"},
    },
)
async def refresh(
        req: Request,
        res: Response,
        service: AuthService = Depends(get_auth_service),
) -> AuthenticationResponse:
    refresh_token = req.cookies.get(security_config.COOKIE_NAME_REFRESH_TOKEN)
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")

    tokens = await service.refresh(refresh_token)
    _set_refresh_token_cookie(res, tokens.refresh_token.token)

    return AuthenticationResponse(
        data=AccessTokenResponse(access_token=tokens.access_token)
    )


@router.post(
    path="/register",
    summary="User registration",
    description="Register a new user",
    response_model=AuthenticationResponse
)
async def register(
        res: Response,
        data: RegistrationRequest,
        service: AuthService = Depends(get_auth_service)) -> AuthenticationResponse:
    tokens = await service.register(
        username=data.username,
        email=data.email,
        password=data.password,
    )

    _set_refresh_token_cookie(res, tokens.refresh_token.token)

    return AuthenticationResponse(
        data=AccessTokenResponse(
            access_token=tokens.access_token
        )
    )


@router.post(
    path="/reset-password",
    summary="Reset password",
    description="Change password for the authenticated user after old password verification.",
    response_model=ResetPasswordResponse,
    responses={
        200: {"description": "Password successfully changed"},
        400: {"description": "Password validation failed"},
        401: {"description": "Authentication required"},
        403: {"description": "Old password is incorrect"},
    },
)
async def reset_password(
        data: ResetPasswordRequest,
        user_id: UUID = Depends(get_current_user_id),
        service: AuthService = Depends(get_auth_service),
) -> ResetPasswordResponse:
    await service.reset_password(
        user_id=user_id,
        old_password=data.old_password,
        new_password=data.new_password,
    )
    return ResetPasswordResponse()

