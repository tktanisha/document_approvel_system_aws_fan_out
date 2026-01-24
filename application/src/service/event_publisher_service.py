import json

import boto3


class EventPublisher:
    def __init__(self, TOPIC_ARN: str):
        self.client = boto3.client("sns")
        self.topic_arn = TOPIC_ARN

    async def publish_status_updated(self, event: dict, consumer: str):
        self.client.publish(
            TopicArn=self.topic_arn,
            Message=json.dumps(event),
            MessageAttributes={
                "consumer": {"DataType": "String", "StringValue": consumer}
            },
        )
