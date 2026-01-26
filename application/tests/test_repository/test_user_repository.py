import unittest
from datetime import datetime
from unittest.mock import MagicMock

import botocore
from enums.user_role import Role
from exceptions.app_exceptions import InternalServerException, UserAlreadyExistsError
from models.user import User
from repository.user_repository import UserRepo


class TestUserRepo(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.mock_dynamodb = MagicMock()
        self.repo = UserRepo(dynamodb=self.mock_dynamodb)

    async def test_find_by_email_success(self):
        self.mock_dynamodb.get_item.return_value = {
            "Item": {
                "pk": {"S": "USER"},
                "sk": {"S": "EMAIL@test@example.com"},
                "id": {"S": "user-1"},
                "name": {"S": "Test User"},
                "email": {"S": "test@example.com"},
                "password_hash": {"S": "hash"},
                "role": {"S": Role.AUTHOR.value},
                "created_at": {"S": datetime.now().isoformat()},
            }
        }

        user = await self.repo.find_by_email("test@example.com")

        self.assertIsNotNone(user)
        self.assertEqual(user.email, "test@example.com")

    async def test_find_by_email_not_found(self):
        self.mock_dynamodb.get_item.return_value = {}

        user = await self.repo.find_by_email("missing@example.com")

        self.assertIsNone(user)

    async def test_find_by_email_exception(self):
        self.mock_dynamodb.get_item.side_effect = Exception("ddb error")

        with self.assertRaises(InternalServerException):
            await self.repo.find_by_email("test@example.com")

    async def test_create_user_success(self):
        user = User(
            id="user-1",
            name="Test User",
            email="test@example.com",
            password_hash="hash",
            role=Role.AUTHOR,
            created_at=datetime.now(),
        )

        self.repo.dynamodb.transact_write_items.return_value = {}

        await self.repo.create_user(user)

        self.repo.dynamodb.transact_write_items.assert_called_once()

    async def test_create_user_already_exists(self):
        user = User(
            id="user-1",
            name="Test User",
            email="test@example.com",
            password_hash="hash",
            role=Role.AUTHOR,
            created_at=datetime.now(),
        )

        error_response = {"Error": {"Code": "ConditionalCheckFailedException"}}

        self.repo.dynamodb.transact_write_items.side_effect = (
            botocore.exceptions.ClientError(error_response, "TransactWriteItems")
        )

        with self.assertRaises(UserAlreadyExistsError):
            await self.repo.create_user(user)

    async def test_find_by_id_success(self):
        self.mock_dynamodb.get_item.return_value = {
            "Item": {
                "pk": {"S": "USER"},
                "sk": {"S": "ID#user-1"},
                "id": {"S": "user-1"},
                "name": {"S": "Test User"},
                "email": {"S": "test@example.com"},
                "password_hash": {"S": "hash"},
                "role": {"S": Role.AUTHOR.value},
                "created_at": {"S": "2024-01-01T10:00:00Z"},
            }
        }

        user = await self.repo.find_by_id("user-1")

        self.assertIsNotNone(user)
        self.assertEqual(user.id, "user-1")

    async def test_find_by_id_not_found(self):
        self.mock_dynamodb.get_item.return_value = {}

        user = await self.repo.find_by_id("missing-id")

        self.assertIsNone(user)

    async def test_find_by_id_exception(self):
        self.mock_dynamodb.get_item.side_effect = Exception("ddb error")

        with self.assertRaises(InternalServerException):
            await self.repo.find_by_id("user-1")
