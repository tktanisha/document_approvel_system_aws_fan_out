import logging
import uuid
from datetime import datetime

from dto.auth import LoginRequest, RegisterRequest
from dto.user import UserResponse
from enums.user_role import Role
from exceptions.app_exceptions import (
    AuthServiceError,
    BadRequestException,
    UserAlreadyExistsError,
)
from helpers.auth_helper import AuthHelper
from models.user import User
from repository.user_repository import UserRepo

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, user_repo: UserRepo):
        self.user_repo = user_repo

    async def register(self, user: RegisterRequest):
        try:
            existing_user = await self.user_repo.find_by_email(user.email)
        except Exception as e:
            logger.exception(e)
            raise AuthServiceError("Failed to verify user") from e

        if existing_user:
            raise UserAlreadyExistsError("User already exists")

        password_hash = AuthHelper.hash_password(user.password)

        user_model: User = User(
            id=str(uuid.uuid4()),
            name=user.name,
            email=user.email,
            password_hash=password_hash,
            role=Role.AUTHOR,
            created_at=datetime.now(),
        )

        try:
            await self.user_repo.create_user(user_model)
        except UserAlreadyExistsError:
            raise
        except Exception as e:
            logger.exception("User creation failed")
            raise AuthServiceError("Failed to register user") from e

    async def login(self, user: LoginRequest):
        try:
            user_db = await self.user_repo.find_by_email(user.email)
        except Exception as e:
            logger.exception("User lookup failed")
            raise AuthServiceError("Login failed") from e

        if not user_db:
            raise BadRequestException("Invalid credentials")

        if not AuthHelper.verify_password(user.password, user_db.password_hash):
            raise BadRequestException("Invalid credentials")

        token = AuthHelper.create_token(
            user_db.id, user_db.role.value, user_db.name, user_db.email
        )

        return token, UserResponse(
            **user_db.model_dump(include={"id", "name", "email", "role", "created_at"})
        )
