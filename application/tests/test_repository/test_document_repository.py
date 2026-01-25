import unittest
from unittest.mock import MagicMock
from datetime import datetime, timezone

from repository.document_repository import DocumentRepo
from enums.document_status import DocumentStatus
from models.document import Document
from exceptions.app_exceptions import InternalServerException


class TestDocumentRepo(unittest.IsolatedAsyncioTestCase):

    @classmethod
    def setUpClass(cls):
        cls.ddb = MagicMock()
        cls.repo = DocumentRepo(dynamodb=cls.ddb)

        # mock serializer to avoid boto type issues
        cls.repo.serializer = MagicMock()
        cls.repo.serializer.serialize.side_effect = lambda v: {"S": str(v)}

        # mock table name to avoid AppSettings dependency
        cls.repo.table = "test-table"

    async def asyncSetUp(self):
        self.ddb.reset_mock()
        self.repo.serializer.reset_mock()

    async def test_update_status_success(self):

        # Arrange
        now = datetime(2026, 1, 1, 10, 0, 0, tzinfo=timezone.utc)

        doc = Document(
            id="doc1",
            author_id="author1",
            status=DocumentStatus.PENDING,
            s3_path="s3://bucket/path",
            comment=None,
            created_at=now,
            updated_at=now,
        )

        self.ddb.transact_write_items.return_value = {}

        # Act
        result = await self.repo.update_status(
            doc=doc,
            new_status=DocumentStatus.APPROVED,
            comment="ok",
            now=now,
        )

        # Assert
        self.assertEqual(result.status, DocumentStatus.APPROVED)
        self.assertEqual(result.author_id, "author1")

        self.ddb.transact_write_items.assert_called_once()

        args = self.ddb.transact_write_items.call_args[1]
        tx = args["TransactItems"]

        # there should be exactly 2 Update operations
        self.assertEqual(len(tx), 2)

        self.assertIn("Update", tx[0])
        self.assertIn("Update", tx[1])

        first_update = tx[0]["Update"]
        second_update = tx[1]["Update"]

        self.assertEqual(first_update["TableName"], "test-table")
        self.assertEqual(second_update["TableName"], "test-table")

        self.assertEqual(
            first_update["Key"]["pk"]["S"],
            "AUTHOR#author1",
        )

        self.assertEqual(
            second_update["Key"]["pk"]["S"],
            "APPROVER#ALL",
        )

    async def test_update_status_transaction_failure(self):

        # Arrange
        now = datetime(2026, 1, 1, 10, 0, 0, tzinfo=timezone.utc)

        doc = Document(
            id="doc1",
            author_id="author1",
            status=DocumentStatus.PENDING,
            s3_path="s3://bucket/path",
            comment=None,
            created_at=now,
            updated_at=now,
        )

        self.ddb.transact_write_items.side_effect = Exception("ddb down")

        # Act + Assert
        with self.assertRaises(InternalServerException):
            await self.repo.update_status(
                doc=doc,
                new_status=DocumentStatus.APPROVED,
                comment="ok",
                now=now,
            )