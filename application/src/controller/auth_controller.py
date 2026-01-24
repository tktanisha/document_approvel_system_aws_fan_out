from typing import Annotated

from fastapi import APIRouter, Depends, status
from src.dto.auth import LoginRequest, RegisterRequest
from src.helpers.api_paths import ApiPaths
from src.helpers.success_response import write_success_response
from src.models.user import User
from src.service.auth_service import AuthService
from src.setup.dependecies.auth_dependency import get_auth_service

router = APIRouter(tags=["Auth"])


@router.post(ApiPaths.AUTH_SIGNUP)
async def signup(
    user_payload: RegisterRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):

    await auth_service.register(user_payload)

    return write_success_response(
        status_code=status.HTTP_201_CREATED, message="User Registeration Successfull"
    )


@router.post(ApiPaths.AUTH_LOGIN)
async def login(
    user_payload: LoginRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):

    token, user = await auth_service.login(user_payload)

    return write_success_response(
        status_code=status.HTTP_200_OK,
        data={
            "token": token,
            "user": {
                "user_name": user.name,
                "role": user.role.value,
            },
        },
        message="login successfully",
    )
