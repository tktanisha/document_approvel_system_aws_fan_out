from pydantic import BaseModel,Field,EmailStr,field_validator
import re

class RegisterRequest(BaseModel):
    model_config = {
        "populate_by_name": True,
        "extra": "forbid",
        "str_strip_whitespace": True,
    }

    name: str = Field(min_lenght=3)
    email: EmailStr
    password:str


    @field_validator("password")
    def _validate_password(cls, v):
        if len(v) < 12:
            raise ValueError("password must be at least 12 characters")
        if not re.search(r"[0-9]", v):
            raise ValueError("password must contain at least one digit")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("password must contain at least one special character")
        if not re.search(r"[A-Z]", v):
            raise ValueError("password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("password must contain at least one lowercase letter")
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
            raise ValueError("password must be at least 12 characters")
        if not re.search(r"[0-9]", v):
            raise ValueError("password must contain at least one digit")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("password must contain at least one special character")
        if not re.search(r"[A-Z]", v):
            raise ValueError("password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("password must contain at least one lowercase letter")
        return v

