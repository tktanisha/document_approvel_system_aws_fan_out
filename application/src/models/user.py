from datetime import datetime

from enums.user_role import Role
from pydantic import BaseModel, EmailStr, Field


class User(BaseModel):
    id: str
    name: str
    email: EmailStr
    password_hash: str
    role: Role = Field(default="AUTHOR")
    created_at: datetime
