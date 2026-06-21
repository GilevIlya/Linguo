from pydantic import BaseModel

from api.v1.schemas.responses.base_response import BaseMessageResponse


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AuthenticationResponse(BaseMessageResponse[AccessTokenResponse]):
    """Response schema for successful login."""
    message: str = "Authentication successful"


class ResetPasswordResponse(BaseMessageResponse[dict]):
    """Response schema for successful password reset."""
    message: str = "Password has been reset successfully"

