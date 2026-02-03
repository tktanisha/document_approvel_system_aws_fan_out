from datetime import datetime

from enums.user_role import Role
from pydantic import BaseModel, EmailStr,Field


class UserResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    role: Role = Field(default=Role.AUTHOR)
    created_at: datetime
