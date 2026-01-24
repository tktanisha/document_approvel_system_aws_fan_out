import json
import logging

from events import handle_event

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    for record in event["Records"]:
        try:
            raw_body = record["body"]

            data = json.loads(raw_body)

            if "Message" in data and isinstance(data["Message"], str):
                body = json.loads(data["Message"])
            else:
                body = data

            event_type = body.get("event_type")
            payload = body.get("payload", {})

            if event_type == "DOCUMENT_STATUS_UPDATED":
                handle_event(event_type=event_type, payload=payload)

            else:
                logger.info(f"Ignoring unknown event_type: {event_type}")

        except Exception as e:
            logger.exception(f"Failed processing notification event {e}")
            raise
