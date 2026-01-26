import unittest
from unittest.mock import patch

from notification_processor.email_service import send_email


class TestEmailService(unittest.TestCase):

    @patch("notification_processor.email_service.ses")
    def test_send_email_success(self, mock_ses):
        mock_ses.send_email.return_value = {
            "MessageId": "msg-123"
        }

        send_email(
            to_email="test@example.com",
            subject="Test Subject",
            body="Test Body",
        )

        mock_ses.send_email.assert_called_once()

    @patch("notification_processor.email_service.ses")
    def test_send_email_no_to_email(self, mock_ses):
        send_email(
            to_email=None,
            subject="Test Subject",
            body="Test Body",
        )

        mock_ses.send_email.assert_not_called()
