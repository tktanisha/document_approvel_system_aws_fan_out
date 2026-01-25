from typing import Annotated

from fastapi import Depends
from repository.user_repository import UserRepo
from service.auth_service import AuthService
from setup.db_connection import get_dynamodb


def get_user_repo(dynamodb=Depends(get_dynamodb)) -> UserRepo:
    return UserRepo(dynamodb=dynamodb)


def get_auth_service(
    user_repo: Annotated[UserRepo, Depends(get_user_repo)]
) -> AuthService:
    return AuthService(user_repo=user_repo)
