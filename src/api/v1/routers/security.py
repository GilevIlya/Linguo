import logging
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from api.v1.services.exceptions.base_exceptions import AuthException
from api.v1.services.exceptions.error_codes.auth_error_codes import AuthErrorCodes
from api.v1.services.utils.jwt import verify_jwt

security = HTTPBearer()

logger = logging.getLogger("app")

def get_current_user_id(cred: Annotated[HTTPAuthorizationCredentials, Depends(security)]) -> UUID:
    jwt = cred.credentials
    token_entity = verify_jwt(jwt)

    if not token_entity:
        logger.warning("Token is invalid")
        raise AuthException(AuthErrorCodes.FORBIDDEN.value, "Jwt is invalid or expired")

    return UUID(token_entity.get("sub"))
