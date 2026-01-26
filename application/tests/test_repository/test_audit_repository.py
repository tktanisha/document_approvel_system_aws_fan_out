import unittest
from datetime import datetime
from unittest.mock import MagicMock

from exceptions.app_exceptions import InternalServerException, NotFoundException
from models.audit_log import AuditLog
from repository.audit_repository import AuditRepo


class TestAuditRepo(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.mock_dynamodb = MagicMock()
        self.repo = AuditRepo(dynamodb=self.mock_dynamodb)

    async def test_get_all_logs_success_without_user_id(self):
        self.mock_dynamodb.query.return_value = {
            "Items": [
                {
                    "pk": {"S": "AUDITLOG"},
                    "sk": {"S": "USER#user-1#EVENT#1"},
                    "doc_id": {"S": "doc-1"},
                    "status": {"S": "PENDING"},
                    "author_id": {"S": "user-1"},
                    "event_type": {"S": "TEST_EVENT"},
                    "timestamp": {"S": datetime.now().isoformat()},
                    "payload": {"S": "{}"},
                }
            ]
        }

        logs = await self.repo.get_all_logs()

        self.assertEqual(len(logs), 1)
        self.assertIsInstance(logs[0], AuditLog)

    async def test_get_all_logs_success_with_user_id(self):
        self.mock_dynamodb.query.return_value = {
            "Items": [
                {
                    "pk": {"S": "AUDITLOG"},
                    "sk": {"S": "USER#user-1#EVENT#2"},
                    "doc_id": {"S": "doc-1"},
                    "status": {"S": "PENDING"},
                    "author_id": {"S": "user-1"},
                    "event_type": {"S": "TEST_EVENT"},
                    "timestamp": {"S": datetime.now().isoformat()},
                    "payload": {"S": "{}"},
                }
            ]
        }

        logs = await self.repo.get_all_logs(user_id="user-1")

        self.assertEqual(len(logs), 1)

    async def test_get_all_logs_not_found(self):
        self.mock_dynamodb.query.return_value = {"Items": []}

        with self.assertRaises(NotFoundException):
            await self.repo.get_all_logs()

    async def test_get_all_logs_ddb_exception(self):
        self.mock_dynamodb.query.side_effect = Exception("ddb error")

        with self.assertRaises(InternalServerException):
            await self.repo.get_all_logs()
