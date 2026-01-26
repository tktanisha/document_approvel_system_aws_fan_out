import unittest
from unittest.mock import MagicMock, patch

from fastapi import HTTPException
from helpers.auth_helper import AuthHelper


class TestAuthHelper(unittest.TestCase):

    def test_hash_and_verify_password_success(self):
        password = "test-password"

        hashed = AuthHelper.hash_password(password)

        self.assertIsNotNone(hashed)
        self.assertTrue(AuthHelper.verify_password(password, hashed))

    def test_verify_password_failure(self):
        password = "test-password"
        wrong_password = "wrong-password"

        hashed = AuthHelper.hash_password(password)

        result = AuthHelper.verify_password(wrong_password, hashed)

        self.assertFalse(result)

    @patch("helpers.auth_helper.jwt.encode")
    def test_create_token_success(self, mock_jwt_encode):
        mock_jwt_encode.return_value = "mock-token"

        token = AuthHelper.create_token(
            user_id="user-1",
            role="AUTHOR",
            name="Test User",
            email="test@example.com",
        )

        self.assertEqual(token, "mock-token")
        mock_jwt_encode.assert_called_once()

    @patch("helpers.auth_helper.jwt.decode")
    def test_verify_jwt_success(self, mock_jwt_decode):
        mock_jwt_decode.return_value = {
            "user_id": "user-1",
            "role": "AUTHOR",
            "email": "test@example.com",
            "name": "Test User",
        }

        request = MagicMock()

        AuthHelper.verify_jwt(request=request, token="valid-token")

        self.assertIsNotNone(request.state.user)
        self.assertEqual(request.state.user["user_id"], "user-1")

    @patch("helpers.auth_helper.jwt.decode")
    def test_verify_jwt_invalid_token(self, mock_jwt_decode):
        from jose import JWTError

        mock_jwt_decode.side_effect = JWTError("invalid")

        request = MagicMock()

        with self.assertRaises(HTTPException):
            AuthHelper.verify_jwt(request=request, token="invalid-token")

    @patch("helpers.auth_helper.jwt.decode")
    def test_verify_jwt_expired_token(self, mock_jwt_decode):
        from jose import ExpiredSignatureError

        mock_jwt_decode.side_effect = ExpiredSignatureError("expired")

        request = MagicMock()

        with self.assertRaises(HTTPException):
            AuthHelper.verify_jwt(request=request, token="expired-token")
