import logging
import uuid
from datetime import datetime

from dto.auth import LoginRequest, RegisterRequest
from dto.user import UserResponse
from enums.user_role import Role
from exceptions.app_exceptions import (
    AuthServiceError,
    BadRequestException,
    NotFoundException,
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
            user_db = await self.user_repo.find_by_email(user.email)
            if user_db:
                raise UserAlreadyExistsError("User Already Exist")

        except NotFoundException:
            pass
        except UserAlreadyExistsError:
            raise

        except Exception as e:
            logger.exception(f"Unexpected error while checking existing user== {e}")
            raise AuthServiceError("Failed to verify existing user") from e

        try:
            password_hash = AuthHelper.hash_password(user.password)
        except Exception as e:
            logger.exception("Password hashing failed")
            raise AuthServiceError("Failed to process password") from e

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
        except Exception as e:
            logger.exception("User creation failed")
            raise AuthServiceError("Failed to register user") from e

    async def login(self, user: LoginRequest):
        try:
            user_db = await self.user_repo.find_by_email(user.email)
        except NotFoundException:
            raise BadRequestException("Invalid credentials")

        except Exception as e:
            logger.exception("Unexpected error during login lookup %s", e)
            raise AuthServiceError("Login failed") from e

        if not AuthHelper.verify_password(user.password, user_db.password_hash):
            logger.info("Invalid password attempt for email=%s", user.email)
            raise BadRequestException("Invalid credentials")

        try:
            token = AuthHelper.create_token(
                user_db.id, user_db.role.value, user_db.name, user_db.email
            )
        except Exception as e:
            logger.exception(f"JWT generation failed : {e}")
            raise AuthServiceError("Failed to generate token") from e

        user: UserResponse = UserResponse(
            **user_db.model_dump(include={"id", "name", "email", "role", "created_at"})
        )
        return token, user
