import unittest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone

from service.document_service import DocumentService
from enums.document_status import DocumentStatus
from exceptions.app_exceptions import (
    BadRequestException,
    ForbiddenException,
    NotFoundException,
    InternalServerException,
    DocumentServiceError,
)


class TestDocumentService(unittest.IsolatedAsyncioTestCase):

    @classmethod
    def setUpClass(cls):
        cls.document_repo = AsyncMock()
        cls.user_repo = AsyncMock()
        cls.audit_repo = AsyncMock()
        cls.event_publisher_service = AsyncMock()

        cls.service = DocumentService(
            document_repo=cls.document_repo,
            audit_repo=cls.audit_repo,
            user_repo=cls.user_repo,
            event_publisher_service=cls.event_publisher_service,
        )

    async def asyncSetUp(self):
        self.document_repo.reset_mock()
        self.user_repo.reset_mock()
        self.event_publisher_service.reset_mock()

        self.document_repo.get_by_id.side_effect = None
        self.document_repo.update_status.side_effect = None

    async def test_update_status_success(self):

        # Arrange
        user_ctx = {
            "user_id": "user1",
            "role": "APPROVER",
            "email": "approval@gmail.com",
        }

        doc_id = "1"
        new_status = DocumentStatus.APPROVED
        comment = "looks good"

        doc = MagicMock()
        doc.status = DocumentStatus.PENDING
        doc.author_id = "user2"

        author = MagicMock()
        author.email = "author@gmail.com"

        updated = MagicMock()
        updated.status = DocumentStatus.APPROVED
        updated.author_id = "user2"
        updated.approver_id = "user1"

        self.document_repo.get_by_id.return_value = doc
        self.document_repo.update_status.return_value = updated
        self.user_repo.find_by_id.return_value = author

        # Act
        result = await self.service.update_status(
            user_ctx=user_ctx,
            document_id=doc_id,
            new_status=new_status,
            comment=comment,
        )

        # Assert
        self.assertEqual(result, updated)

        self.document_repo.get_by_id.assert_awaited_once_with(doc_id)
        self.document_repo.update_status.assert_awaited_once()
        self.user_repo.find_by_id.assert_awaited_once_with("user2")

        self.assertEqual(
            self.event_publisher_service.publish_status_updated.await_count,
            2,
        )

    async def test_update_status_invalid_user_ctx(self):
        with self.assertRaises(BadRequestException):
            await self.service.update_status(
                user_ctx=None,
                document_id="doc1",
                new_status=DocumentStatus.APPROVED,
                comment=None,
            )     

    async def test_update_status_non_approver_role(self):
        user_ctx = {
        "user_id": "user1",
        "role": "AUTHOR",
        }


        with self.assertRaises(ForbiddenException):
            await self.service.update_status(
            user_ctx=user_ctx,
            document_id="doc1",
            new_status=DocumentStatus.APPROVED,
            comment=None,
        )


    async def test_update_status_document_not_found(self):
        self.document_repo.get_by_id.side_effect = NotFoundException("not found")
        user_ctx = {
        "user_id": "user1",
        "role": "APPROVER",
        }

        with self.assertRaises(NotFoundException):
            await self.service.update_status(
            user_ctx=user_ctx,
            document_id="doc1",
            new_status=DocumentStatus.APPROVED,
            comment=None,
        )


    async def test_update_status_invalid_transition_from_pending(self):
        doc = AsyncMock()
        doc.status = DocumentStatus.PENDING        
        self.document_repo.get_by_id.return_value = doc
        user_ctx = {
        "user_id": "user1",
        "role": "APPROVER",
        }

        with self.assertRaises(BadRequestException):
            await self.service.update_status(
            user_ctx=user_ctx,
            document_id="doc1",
            new_status=DocumentStatus.PENDING,
            comment=None,
        )


    async def test_update_status_update_repo_failure(self):
        doc = AsyncMock()
        doc.status = DocumentStatus.PENDING
        doc.author_id = "author1"
        
        user_ctx = {
        "user_id": "user1",
        "role": "APPROVER",
        }

        self.document_repo.get_by_id.return_value = doc
        self.document_repo.update_status.side_effect = Exception("db down")


        with self.assertRaises(DocumentServiceError):
            await self.service.update_status(
            user_ctx=user_ctx,
            document_id="doc1",
            new_status=DocumentStatus.APPROVED,
            comment=None,
        )
            