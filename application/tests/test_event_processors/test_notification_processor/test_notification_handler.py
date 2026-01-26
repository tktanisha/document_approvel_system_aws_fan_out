import unittest
import json
from unittest.mock import patch

from notification_processor.handler import lambda_handler


class TestNotificationLambdaHandler(unittest.TestCase):

    @patch("notification_processor.handler.handle_event")
    def test_document_status_updated_event(self, mock_handle_event):
        event = {
            "Records": [
                {
                    "body": json.dumps({
                        "event_type": "DOCUMENT_STATUS_UPDATED",
                        "payload": {
                            "doc_id": "doc-1",
                            "status": "APPROVED"
                        }
                    })
                }
            ]
        }

        lambda_handler(event, context=None)

        mock_handle_event.assert_called_once_with(
            event_type="DOCUMENT_STATUS_UPDATED",
            payload={
                "doc_id": "doc-1",
                "status": "APPROVED"
            }
        )

    @patch("notification_processor.handler.handle_event")
    def test_sns_wrapped_message(self, mock_handle_event):
        inner_message = {
            "event_type": "DOCUMENT_STATUS_UPDATED",
            "payload": {
                "doc_id": "doc-2"
            }
        }

        event = {
            "Records": [
                {
                    "body": json.dumps({
                        "Message": json.dumps(inner_message)
                    })
                }
            ]
        }

        lambda_handler(event, context=None)

        mock_handle_event.assert_called_once()

    @patch("notification_processor.handler.handle_event")
    def test_unknown_event_type(self, mock_handle_event):
        event = {
            "Records": [
                {
                    "body": json.dumps({
                        "event_type": "SOME_OTHER_EVENT",
                        "payload": {}
                    })
                }
            ]
        }

        lambda_handler(event, context=None)

        mock_handle_event.assert_not_called()

    def test_invalid_json_raises_exception(self):
        event = {
            "Records": [
                {
                    "body": "not-a-json"
                }
            ]
        }

        with self.assertRaises(Exception):
            lambda_handler(event, context=None)
