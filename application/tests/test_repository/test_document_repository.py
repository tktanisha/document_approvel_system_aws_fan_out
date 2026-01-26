import unittest
from datetime import datetime
from unittest.mock import MagicMock

import botocore
from enums.document_status import DocumentStatus
from exceptions.app_exceptions import InternalServerException, NotFoundException
from models.document import Document
from repository.document_repository import DocumentRepo


class TestDocumentRepo(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.mock_dynamodb = MagicMock()
        self.repo = DocumentRepo(dynamodb=self.mock_dynamodb)

    async def test_create_document_success(self):
        doc = Document(
            id="doc-1",
            author_id="user-1",
            status=DocumentStatus.PENDING,
            s3_path="s3://bucket/file",
            comment=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        self.mock_dynamodb.transact_write_items.return_value = {}

        await self.repo.create_document(doc)

        self.mock_dynamodb.transact_write_items.assert_called_once()

    async def test_create_document_ddb_error(self):
        doc = Document(
            id="doc-1",
            author_id="user-1",
            status=DocumentStatus.PENDING,
            s3_path="s3://bucket/file",
            comment=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        self.mock_dynamodb.transact_write_items.side_effect = (
            botocore.exceptions.ClientError(
                {"Error": {"Code": "InternalError"}}, "TransactWriteItems"
            )
        )

        with self.assertRaises(InternalServerException):
            await self.repo.create_document(doc)

    async def test_get_documents_author_success(self):
        user_ctx = {
            "user_id": "user-1",
            "role": "AUTHOR",
        }

        self.mock_dynamodb.query.return_value = {
            "Items": [
                {
                    "id": {"S": "doc-1"},
                    "author_id": {"S": "user-1"},
                    "status": {"S": "PENDING"},
                    "s3_path": {"S": "s3://bucket/file"},
                    "comment": {"NULL": True},
                    "created_at": {"S": datetime.now().isoformat()},
                    "updated_at": {"S": datetime.now().isoformat()},
                }
            ]
        }

        docs = await self.repo.get_documents(user_ctx, status=None)

        self.assertEqual(len(docs), 1)
        self.assertEqual(docs[0].id, "doc-1")

    async def test_get_documents_not_found(self):
        user_ctx = {
            "user_id": "user-1",
            "role": "AUTHOR",
        }

        self.mock_dynamodb.query.return_value = {"Items": []}

        with self.assertRaises(NotFoundException):
            await self.repo.get_documents(user_ctx, status=None)

    async def test_get_by_id_success(self):
        self.mock_dynamodb.get_item.return_value = {
            "Item": {
                "id": {"S": "doc-1"},
                "author_id": {"S": "user-1"},
                "status": {"S": "PENDING"},
                "s3_path": {"S": "s3://bucket/file"},
                "comment": {"NULL": True},
                "created_at": {"S": "2024-01-01T10:00:00Z"},
                "updated_at": {"S": "2024-01-01T10:00:00Z"},
            }
        }

        doc = await self.repo.get_by_id("doc-1")

        self.assertEqual(doc.id, "doc-1")
        self.assertEqual(doc.status, DocumentStatus.PENDING)

    async def test_get_by_id_not_found(self):
        self.mock_dynamodb.get_item.return_value = {}

        with self.assertRaises(NotFoundException):
            await self.repo.get_by_id("missing-doc")

    async def test_update_status_success(self):
        doc = Document(
            id="doc-1",
            author_id="user-1",
            status=DocumentStatus.PENDING,
            s3_path="s3://bucket/file",
            comment=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        now = datetime.now()

        self.mock_dynamodb.transact_write_items.return_value = {}

        updated = await self.repo.update_status(
            doc=doc,
            new_status=DocumentStatus.APPROVED,
            comment="ok",
            now=now,
        )

        self.assertEqual(updated.status, DocumentStatus.APPROVED)
        self.mock_dynamodb.transact_write_items.assert_called_once()

    async def test_update_status_ddb_error(self):
        doc = Document(
            id="doc-1",
            author_id="user-1",
            status=DocumentStatus.PENDING,
            s3_path="s3://bucket/file",
            comment=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        self.mock_dynamodb.transact_write_items.side_effect = Exception("ddb error")

        with self.assertRaises(InternalServerException):
            await self.repo.update_status(
                doc=doc,
                new_status=DocumentStatus.REJECTED,
                comment="no",
                now=datetime.now(),
            )
