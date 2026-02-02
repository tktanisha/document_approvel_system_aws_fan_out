import json
import unittest
from unittest.mock import patch

import botocore
from audit_processor.handler import lambda_handler, write_audit_log


class TestAuditLambda(unittest.TestCase):

    @patch("audit_processor.handler.dynamodb")
    def test_lambda_handler_success(self, mock_dynamodb):
        event = {
            "Records": [
                {
                    "body": json.dumps(
                        {
                            "Message": json.dumps(
                                {
                                    "event_id": "event-1",
                                    "event_type": "DOCUMENT_STATUS_UPDATED",
                                    "payload": {
                                        "doc_id": "doc-1",
                                        "author_id": "user-1",
                                        "new_status": "APPROVED",
                                        "timestamp": "2024-01-01T10:00:00Z",
                                    },
                                }
                            )
                        }
                    )
                }
            ]
        }

        lambda_handler(event, context=None)

        mock_dynamodb.put_item.assert_called_once()

    @patch("audit_processor.handler.dynamodb")
    def test_duplicate_event_ignored(self, mock_dynamodb):
        error_response = {"Error": {"Code": "ConditionalCheckFailedException"}}

        mock_dynamodb.put_item.side_effect = botocore.exceptions.ClientError(
            error_response, "PutItem"
        )

        write_audit_log(
            event_id="event-1",
            event_type="DOCUMENT_STATUS_UPDATED",
            payload={
                "doc_id": "doc-1",
                "author_id": "user-1",
                "status": "APPROVED",
                "timestamp": "2024-01-01T10:00:00Z",
            },
        )

        mock_dynamodb.put_item.assert_called_once()

    def test_lambda_handler_missing_message(self):
        event = {"Records": [{"body": json.dumps({"foo": "bar"})}]}

        with self.assertRaises(Exception):
            lambda_handler(event, context=None)

    @patch("audit_processor.handler.dynamodb")
    def test_write_audit_log_ddb_failure(self, mock_dynamodb):
        mock_dynamodb.put_item.side_effect = Exception("ddb down")

        with self.assertRaises(Exception):
            write_audit_log(
                event_id="event-2",
                event_type="DOCUMENT_STATUS_UPDATED",
                payload={
                    "doc_id": "doc-2",
                    "author_id": "user-2",
                    "status": "REJECTED",
                    "timestamp": "2024-01-01T10:00:00Z",
                },
            )
