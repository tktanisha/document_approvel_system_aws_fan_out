import unittest
from datetime import datetime
from unittest.mock import AsyncMock, Mock

from controller.documents_controller import router
from enums.document_status import DocumentStatus
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from helpers.api_paths import ApiPaths
from helpers.auth_helper import AuthHelper
from models.document import Document
from setup.dependecies.document_dependency import get_document_service


class TestDocumentController(unittest.TestCase):

    def setUp(self):
        app = FastAPI()

        def mock_verify_jwt(request: Request, token: str = None):
            request.state.user = {
                "user_id": "user-1",
                "role": "AUTHOR",
            }

        app.dependency_overrides[AuthHelper.verify_jwt] = mock_verify_jwt

        app.include_router(router)

        self.mock_document_service = Mock()
        self.mock_document_service.get_all_document = AsyncMock()
        self.mock_document_service.create_document = AsyncMock()
        self.mock_document_service.update_status = AsyncMock()

        app.dependency_overrides[get_document_service] = (
            lambda: self.mock_document_service
        )

        self.mock_presigned_service = Mock()
        self.mock_presigned_service.generate_presigned_get_url = AsyncMock(
            return_value="mock-url"
        )

        app.dependency_overrides["service.presigned_service.PresignedService"] = (
            lambda: self.mock_presigned_service
        )

        self.client = TestClient(app)

    def test_get_all_documents_success(self):
        mock_doc = Mock()
        mock_doc.id = "doc-1"
        mock_doc.author_id = "user-1"
        mock_doc.status = DocumentStatus.PENDING
        mock_doc.s3_path = "s3://my-doc-approval-bucket/documents/1/file.pdf"
        mock_doc.created_at = datetime.now()
        mock_doc.updated_at = datetime.now()
        mock_doc.model_dump.return_value = {
            "id": "doc-1",
            "author_id": "user-1",
            "status": DocumentStatus.PENDING,
            "comment": None,
        }

        self.mock_document_service.get_all_document.return_value = [mock_doc]

        response = self.client.get(ApiPaths.GET_ALL_DOCUMENTS)

        self.assertEqual(response.status_code, 200)
        self.assertIn("data", response.json())
        self.mock_document_service.get_all_document.assert_called_once()

    def test_create_document_success(self):
        payload = {
            "document_id": "doc-1",
            "file_key": "documents/1/file.pdf",
        }

        response = self.client.post(ApiPaths.UPLOAD_DOCUMENT, json=payload)

        self.assertEqual(response.status_code, 201)
        self.mock_document_service.create_document.assert_called_once()

    def test_update_document_status_success(self):
        mock_doc = Mock(spec=Document)
        mock_doc.id = "doc-1"
        mock_doc.author_id = "user-1"
        mock_doc.status = DocumentStatus.APPROVED
        mock_doc.s3_path = "s3://bucket/file"
        mock_doc.comment = "ok"
        mock_doc.created_at = datetime.now()
        mock_doc.updated_at = datetime.now()
        mock_doc.model_dump.return_value = {
            "id": "doc-1",
            "author_id": "user-1",
            "status": DocumentStatus.APPROVED,
            "comment": "ok",
        }

        self.mock_document_service.update_status.return_value = mock_doc

        payload = {
            "status": "APPROVED",
            "comment": "ok",
        }

        response = self.client.patch(
            ApiPaths.UPDATE_DOCUMENT_STATUS.format(document_id="doc-1"),
            json=payload,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("data", response.json())
        self.mock_document_service.update_status.assert_called_once()
