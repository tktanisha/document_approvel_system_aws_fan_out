import unittest
from unittest.mock import AsyncMock, MagicMock

from enums.user_role import Role
from exceptions.app_exceptions import AuditServiceError, BadRequestException
from service.audit_service import AuditService


class TestAuditService(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.audit_repo = MagicMock()
        self.audit_repo.get_all_logs = AsyncMock()

        self.service = AuditService(audit_repo=self.audit_repo)

    async def test_get_all_audit_logs_author_success(self):
        user_ctx = {
            "user_id": "user-1",
            "role": Role.AUTHOR.value,
        }

        mock_logs = [MagicMock()]
        self.audit_repo.get_all_logs.return_value = mock_logs

        result = await self.service.get_all_audit_logs(user_ctx)

        self.audit_repo.get_all_logs.assert_called_once_with(user_id="user-1")
        self.assertEqual(result, mock_logs)

    async def test_get_all_audit_logs_approver_success(self):
        user_ctx = {
            "user_id": "user-2",
            "role": Role.APPROVER.value,
        }

        mock_logs = [MagicMock(), MagicMock()]
        self.audit_repo.get_all_logs.return_value = mock_logs

        result = await self.service.get_all_audit_logs(user_ctx)

        self.audit_repo.get_all_logs.assert_called_once_with()
        self.assertEqual(result, mock_logs)

    async def test_get_all_audit_logs_no_user_context(self):
        with self.assertRaises(BadRequestException):
            await self.service.get_all_audit_logs(None)

    async def test_get_all_audit_logs_missing_role(self):
        user_ctx = {"user_id": "user-1"}

        with self.assertRaises(BadRequestException):
            await self.service.get_all_audit_logs(user_ctx)

    async def test_get_all_audit_logs_author_missing_user_id(self):
        user_ctx = {"role": Role.AUTHOR.value}

        with self.assertRaises(AuditServiceError):
            await self.service.get_all_audit_logs(user_ctx)

    async def test_get_all_audit_logs_invalid_role(self):
        user_ctx = {"user_id": "user-1", "role": "VIEWER"}

        with self.assertRaises(AuditServiceError):
            await self.service.get_all_audit_logs(user_ctx)

    async def test_get_all_audit_logs_repo_exception(self):
        user_ctx = {
            "user_id": "user-1",
            "role": Role.APPROVER.value,
        }

        self.audit_repo.get_all_logs.side_effect = Exception("db error")

        with self.assertRaises(AuditServiceError):
            await self.service.get_all_audit_logs(user_ctx)
