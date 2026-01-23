
from fastapi import Depends
from typing import Annotated
from src.repository.user_repository import UserRepo
from src.setup.db_connection import get_dynamodb
from src.service.auth_service import AuthService


def get_user_repo(
        dynamodb = Depends(get_dynamodb)
) -> UserRepo:
    return UserRepo(dynamodb = dynamodb) 


def get_auth_service(
        user_repo: Annotated[UserRepo , Depends(get_user_repo)]
) -> AuthService:
    return AuthService(user_repo = user_repo) 




