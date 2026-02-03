import re

from pydantic import BaseModel, EmailStr, Field, field_validator
from helpers.common import Common

class RegisterRequest(BaseModel):
    model_config = {
        "populate_by_name": True,
        "extra": "forbid",
        "str_strip_whitespace": True,
    }

    name: str = Field(min_lenght=3)
    email: EmailStr
    password: str

    @field_validator("password")
    def _validate_password(cls, v):
        if len(v) < 12:
            raise ValueError(Common.PASSWORD_MIN_LENGTH)
        if not re.search(r"[0-9]", v):
            raise ValueError(Common.PASSWORD_MUST_CONTAIN_DIGIT)
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError(Common.PASSWORD_MUST_CONTAIN_SPECIAL_CHAR)
        if not re.search(r"[A-Z]", v):
            raise ValueError(Common.PASSWORD_MUST_CONTAIN_UPPERCASE)
        if not re.search(r"[a-z]", v):
            raise ValueError(Common.PASSWORD_MUST_CONTAIN_LOWERCASE)
        return v


class LoginRequest(BaseModel):
    model_config = {
        "populate_by_name": True,
        "extra": "forbid",
        "str_strip_whitespace": True,
    }

    email: EmailStr
    password: str = Field(min_length=12)

    @field_validator("password")
    def _validate_password(cls, v):
        if len(v) < 12:
            raise ValueError(Common.PASSWORD_MIN_LENGTH)
        if not re.search(r"[0-9]", v):
            raise ValueError(Common.PASSWORD_MUST_CONTAIN_DIGIT)
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError(Common.PASSWORD_MUST_CONTAIN_SPECIAL_CHAR)
        if not re.search(r"[A-Z]", v):
            raise ValueError(Common.PASSWORD_MUST_CONTAIN_UPPERCASE)
        if not re.search(r"[a-z]", v):
            raise ValueError(Common.PASSWORD_MUST_CONTAIN_LOWERCASE)
        return v
