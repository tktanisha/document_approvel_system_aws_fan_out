import unittest
from unittest.mock import patch

from notification_processor.events import handle_event, handle_status_update


class TestEvents(unittest.TestCase):

    @patch("notification_processor.events.send_email")
    def test_handle_event_document_status_updated(self, mock_send_email):
        payload = {
            "author_email": "test@example.com",
            "doc_id": "doc-1",
            "new_status": "APPROVED",
            "comment": "Looks good",
        }

        handle_event(
            event_type="DOCUMENT_STATUS_UPDATED",
            payload=payload,
        )

        mock_send_email.assert_called_once()

    @patch("notification_processor.events.send_email")
    def test_handle_event_unknown_type(self, mock_send_email):
        handle_event(
            event_type="SOME_OTHER_EVENT",
            payload={},
        )

        mock_send_email.assert_not_called()

    @patch("notification_processor.events.send_email")
    def test_handle_status_update_sends_email(self, mock_send_email):
        payload = {
            "author_email": "test@example.com",
            "doc_id": "doc-2",
            "new_status": "REJECTED",
            "comment": None,
        }

        handle_status_update(payload)

        mock_send_email.assert_called_once()

        args, kwargs = mock_send_email.call_args
        self.assertEqual(args[0], "test@example.com")
        self.assertIn("doc-2", args[1])
