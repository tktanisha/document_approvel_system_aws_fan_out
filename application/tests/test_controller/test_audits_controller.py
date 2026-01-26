import unittest
from datetime import datetime
from unittest.mock import AsyncMock, Mock

from controller.audits_controller import router
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from helpers.api_paths import ApiPaths
from helpers.auth_helper import AuthHelper
from setup.dependecies.audit_dependency import get_audit_service


class TestAuditController(unittest.TestCase):

    def setUp(self):
        app = FastAPI()

        def mock_verify_jwt(request: Request, token: str = None):
            request.state.user = {
                "user_id": "user-1",
                "role": "AUTHOR",
            }

        app.dependency_overrides[AuthHelper.verify_jwt] = mock_verify_jwt

        app.include_router(router)

        self.mock_audit_service = Mock()
        self.mock_audit_service.get_all_audit_logs = AsyncMock()

        app.dependency_overrides[get_audit_service] = lambda: self.mock_audit_service

        self.client = TestClient(app)

    def test_get_audit_logs_success(self):
        mock_auditlog = Mock()
        mock_auditlog.timestamp = datetime.now()
        mock_auditlog.model_dump.return_value = {
            "doc_id": "doc-1",
            "status": "PENDING",
            "author_id": "user-1",
            "event_type": "TEST_EVENT",
            "payload": "{}",
        }

        self.mock_audit_service.get_all_audit_logs.return_value = [mock_auditlog]

        response = self.client.get(ApiPaths.GET_AUDIT_LOGS)

        self.assertIn("data", response.json())
        self.assertEqual(response.status_code, 200)
        self.mock_audit_service.get_all_audit_logs.assert_called_once()
