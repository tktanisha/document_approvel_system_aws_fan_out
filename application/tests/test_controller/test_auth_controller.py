import unittest
from unittest.mock import AsyncMock, Mock

from controller.auth_controller import router
from enums.user_role import Role
from fastapi import FastAPI
from fastapi.testclient import TestClient
from helpers.api_paths import ApiPaths
from setup.dependecies.auth_dependency import get_auth_service


class TestAuthController(unittest.TestCase):

    def setUp(self):
        app = FastAPI()

        app.include_router(router)

        self.mock_auth_service = Mock()
        self.mock_auth_service.register = AsyncMock()
        self.mock_auth_service.login = AsyncMock()

        app.dependency_overrides[get_auth_service] = lambda: self.mock_auth_service

        self.client = TestClient(app)

    def test_signup_success(self):
        payload = {
            "name": "Test User",
            "email": "test@example.com",
            "password": "Password123@",
        }

        response = self.client.post(ApiPaths.AUTH_SIGNUP, json=payload)

        self.assertEqual(response.status_code, 201)
        self.mock_auth_service.register.assert_called_once()

    def test_login_success(self):
        mock_user = Mock()
        mock_user.name = "Test User"
        mock_user.role = Role.AUTHOR

        self.mock_auth_service.login.return_value = (
            "mock-token",
            mock_user,
        )

        payload = {
            "email": "test@example.com",
            "password": "Password123@",
        }

        response = self.client.post(ApiPaths.AUTH_LOGIN, json=payload)

        self.assertEqual(response.status_code, 200)
        self.assertIn("data", response.json())
        self.mock_auth_service.login.assert_called_once()
