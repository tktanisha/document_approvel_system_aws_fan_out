import unittest
from unittest.mock import AsyncMock, Mock

from controller.presigned_controller import router
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from helpers.api_paths import ApiPaths
from helpers.auth_helper import AuthHelper
from service.presigned_service import PresignedService


class TestPresignedController(unittest.TestCase):

    def setUp(self):
        app = FastAPI()

        def mock_verify_jwt(request: Request, token: str = None):
            request.state.user = {
                "user_id": "user-1",
                "role": "AUTHOR",
            }

        app.dependency_overrides[AuthHelper.verify_jwt] = mock_verify_jwt

        app.include_router(router)

        # mock presigned service
        self.mock_presigned_service = Mock()
        self.mock_presigned_service.generate_presigned_url = AsyncMock()

        app.dependency_overrides[PresignedService] = lambda: self.mock_presigned_service

        self.client = TestClient(app)

    def test_generate_presigned_url_success(self):
        self.mock_presigned_service.generate_presigned_url.return_value = Mock(
            model_dump=Mock(
                return_value={
                    "document_id": "doc-1",
                    "upload_url": "mock-upload-url",
                    "file_key": "documents/doc-1/file.pdf",
                }
            )
        )

        payload = {
            "filename": "file.pdf",
            "content_type": "application/pdf",
        }

        response = self.client.post(ApiPaths.PRESIGNED_URL, json=payload)

        self.assertEqual(response.status_code, 200)
        self.assertIn("data", response.json())
        self.mock_presigned_service.generate_presigned_url.assert_called_once()
