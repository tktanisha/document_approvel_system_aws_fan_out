from datetime import datetime

from pydantic import BaseModel, EmailStr
from src.enums.user_role import Role


class UserResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    role: Role
    created_at: datetime
