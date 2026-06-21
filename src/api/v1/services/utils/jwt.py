from dataclasses import dataclass, field, asdict
from datetime import datetime
from json import loads

from jose import jwt, jws, ExpiredSignatureError, JWTError  # type: ignore[import-untyped]

from api.v1.configs.security_config import security_config as cfg


@dataclass(frozen=True)
class JWTPayload:
    sub: str
    exp: datetime
    iat: datetime = field(default_factory=datetime.now)

def sign_jwt(payload: JWTPayload) -> str:
    to_dict = asdict(payload)
    return jwt.encode(to_dict, cfg.SECRET_KEY, algorithm=cfg.ALGORITHM)

def verify_jwt(token: str) -> dict | None:
    try:
        return loads(jws.verify(token, cfg.SECRET_KEY, algorithms=[cfg.ALGORITHM]).decode())
    except (JWTError, ExpiredSignatureError, Exception):
        return None
