import unittest
from unittest.mock import AsyncMock, MagicMock

from dto.document import CreateDocumentRequest
from enums.document_status import DocumentStatus
from exceptions.app_exceptions import BadRequestException, ForbiddenException
from models.document import Document
from service.document_service import DocumentService


class TestDocumentService(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.document_repo = MagicMock()
        self.audit_repo = MagicMock()
        self.user_repo = MagicMock()
        self.event_publisher = MagicMock()

        self.document_repo.create_document = AsyncMock()
        self.document_repo.get_documents = AsyncMock()
        self.document_repo.get_by_id = AsyncMock()
        self.document_repo.update_status = AsyncMock()

        self.user_repo.find_by_id = AsyncMock()
        self.event_publisher.publish_status_updated = AsyncMock()

        self.service = DocumentService(
            document_repo=self.document_repo,
            audit_repo=self.audit_repo,
            user_repo=self.user_repo,
            event_publisher_service=self.event_publisher,
        )

        self.user_ctx = {
            "user_id": "user-123",
            "role": "APPROVER",
        }

    async def test_create_document_success(self):
        doc_request = CreateDocumentRequest(document_id="doc-1", file_key="file.pdf")

        await self.service.create_document(self.user_ctx, doc_request)

        self.document_repo.create_document.assert_called_once()
        self.event_publisher.publish_status_updated.assert_called_once()

    async def test_create_document_no_user_context(self):
        doc_request = CreateDocumentRequest(document_id="doc-1", file_key="file.pdf")

        with self.assertRaises(BadRequestException):
            await self.service.create_document(None, doc_request)

    async def test_get_all_document_success(self):
        mock_docs = [MagicMock(spec=Document)]
        self.document_repo.get_documents.return_value = mock_docs

        result = await self.service.get_all_document(self.user_ctx)

        self.document_repo.get_documents.assert_called_once()
        self.assertEqual(result, mock_docs)

    async def test_get_all_document_missing_user_id(self):
        bad_ctx = {}

        with self.assertRaises(BadRequestException):
            await self.service.get_all_document(bad_ctx)

    async def test_update_status_success(self):
        doc = MagicMock(spec=Document)
        doc.status = DocumentStatus.PENDING
        doc.author_id = "author-1"

        updated_doc = MagicMock(spec=Document)

        self.document_repo.get_by_id.return_value = doc
        self.document_repo.update_status.return_value = updated_doc

        author = MagicMock()
        author.email = "test@example.com"
        self.user_repo.find_by_id.return_value = author

        result = await self.service.update_status(
            user_ctx=self.user_ctx,
            document_id="doc-1",
            new_status=DocumentStatus.APPROVED,
            comment="ok",
        )

        self.assertEqual(result, updated_doc)
        self.document_repo.update_status.assert_called_once()
        self.event_publisher.publish_status_updated.assert_called()

    async def test_update_status_not_approver(self):
        bad_ctx = {"user_id": "user-123", "role": "VIEWER"}

        with self.assertRaises(ForbiddenException):
            await self.service.update_status(
                user_ctx=bad_ctx,
                document_id="doc-1",
                new_status=DocumentStatus.APPROVED,
                comment=None,
            )
