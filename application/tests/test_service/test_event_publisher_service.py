import json
import unittest
from unittest.mock import MagicMock, patch

from service.event_publisher_service import EventPublisher


class TestEventPublisher(unittest.IsolatedAsyncioTestCase):

    @patch("service.event_publisher_service.boto3.client")
    async def test_publish_status_updated_success(self, mock_boto_client):
        mock_sns_client = MagicMock()
        mock_boto_client.return_value = mock_sns_client

        topic_arn = "mockarn"
        publisher = EventPublisher(TOPIC_ARN=topic_arn)

        event = {
            "event_id": "event-1",
            "event_type": "TEST_EVENT",
            "payload": {"key": "value"},
        }

        await publisher.publish_status_updated(event=event, consumer="AUDIT")

        mock_boto_client.assert_called_once_with("sns")
        mock_sns_client.publish.assert_called_once()

        args, kwargs = mock_sns_client.publish.call_args

        self.assertEqual(kwargs["TopicArn"], topic_arn)
        self.assertEqual(json.loads(kwargs["Message"]), event)
