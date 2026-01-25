from datetime import datetime

from pydantic import BaseModel, EmailStr, Field
from enums.user_role import Role


class User(BaseModel):
    id: str
    name: str
    email: EmailStr
    password_hash: str
    role: Role = Field(default="AUTHOR")
    created_at: datetime
