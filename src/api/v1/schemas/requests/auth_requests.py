import re

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator


def validate_password_strength(password: str) -> str:
    if len(password) < 8:
        raise ValueError("Password too short")
    if not re.search(r"[A-Z]", password):
        raise ValueError("Must contain at least one uppercase letter")
    if not re.search(r"[a-z]", password):
        raise ValueError("Must contain at least one lowercase letter")
    if not re.search(r"\d", password):
        raise ValueError("Must contain at least one digit")
    return password


class AuthenticationRequest(BaseModel):
    email: EmailStr = Field(max_length=255)
    password: str


class RegistrationRequest(AuthenticationRequest):
    username: str = Field(max_length=55, min_length=3, kw_only=True)

    @field_validator("password")
    def check_password(cls, v: str) -> str:
        return validate_password_strength(v)


class ResetPasswordRequest(BaseModel):
    old_password: str
    new_password: str
    confirmed_password: str

    @field_validator("new_password")
    def check_new_password_strength(cls, v: str) -> str:
        return validate_password_strength(v)

    @model_validator(mode="after")
    def check_passwords_match(self) -> "ResetPasswordRequest":
        if self.new_password != self.confirmed_password:
            raise ValueError("new_password and confirmed_password must match")
        return self
