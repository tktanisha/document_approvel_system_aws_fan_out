import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from dto.auth import LoginRequest, RegisterRequest
from enums.user_role import Role
from exceptions.app_exceptions import (
    AuthServiceError,
    BadRequestException,
    UserAlreadyExistsError,
)
from models.user import User
from service.auth_service import AuthService


class TestAuthService(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.user_repo = MagicMock()
        self.user_repo.find_by_email = AsyncMock()
        self.user_repo.create_user = AsyncMock()

        self.auth_service = AuthService(user_repo=self.user_repo)

    @patch("service.auth_service.AuthHelper.hash_password")
    async def test_register_success(self, mock_hash_password):
        mock_hash_password.return_value = "hashed-password"

        self.user_repo.find_by_email.return_value = None

        user_req = RegisterRequest(
            name="Test User", email="test@example.com", password="Password123@"
        )

        await self.auth_service.register(user_req)

        self.user_repo.create_user.assert_called_once()
        mock_hash_password.assert_called_once_with("Password123@")

    async def test_register_user_already_exists(self):
        self.user_repo.find_by_email.return_value = MagicMock()

        user_req = RegisterRequest(
            name="Test User", email="test@example.com", password="Password123@"
        )

        with self.assertRaises(UserAlreadyExistsError):
            await self.auth_service.register(user_req)

    async def test_login_success(self):
        mock_user = MagicMock(spec=User)
        mock_user.id = "user-1"
        mock_user.name = "Test User"
        mock_user.email = "test@example.com"
        mock_user.role = Role.AUTHOR
        mock_user.password_hash = "hashed-password"
        mock_user.created_at = MagicMock()
        mock_user.model_dump.return_value = {
            "id": "user-1",
            "name": "Test User",
            "email": "test@example.com",
            "role": Role.AUTHOR,
            "created_at": mock_user.created_at,
        }

        self.user_repo.find_by_email.return_value = mock_user

        with patch(
            "service.auth_service.AuthHelper.verify_password"
        ) as mock_verify, patch(
            "service.auth_service.AuthHelper.create_token"
        ) as mock_create_token:

            mock_verify.return_value = True
            mock_create_token.return_value = "jwt-token"

            login_req = LoginRequest(email="test@example.com", password="Password123@")

            token, user_resp = await self.auth_service.login(login_req)

            self.assertEqual(token, "jwt-token")
            mock_verify.assert_called_once()
            mock_create_token.assert_called_once()

    async def test_login_invalid_credentials(self):
        self.user_repo.find_by_email.return_value = None

        login_req = LoginRequest(email="test@example.com", password="Password123@")

        with self.assertRaises(BadRequestException):
            await self.auth_service.login(login_req)

    async def test_login_repo_exception(self):
        self.user_repo.find_by_email.side_effect = Exception("db down")

        login_req = LoginRequest(email="test@example.com", password="Password123@")

        with self.assertRaises(AuthServiceError):
            await self.auth_service.login(login_req)
