import json
import logging
import os

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.client("dynamodb")
TABLE_NAME = os.environ.get("DDB_TABLE_NAME")


def lambda_handler(event, context):
    for record in event["Records"]:
        try:
            envelope = json.loads(record["body"])

            message_str = envelope.get("Message")

            if not message_str:
                raise ValueError("No Message field in SNS envelope")

            body = json.loads(message_str)

            event_id = body["event_id"]
            event_type = body["event_type"]
            payload = body["payload"]

            write_audit_log(event_id, event_type, payload)

        except Exception:
            logger.exception("Failed processing audit event")
            raise  


def write_audit_log(event_id: str, event_type: str, payload: dict):
    author_id = payload.get("author_id")
    approver_id = payload.get("approver_id")
    doc_id = payload.get("doc_id")
    status = payload.get("new_status") or payload.get("status")
    comment = payload.get("comment")
    timestamp = payload.get("timestamp")

    pk = "AUDITLOG"
    sk = f"USER#{author_id}#EVENT#{event_id}"

    item = {
        "pk": {"S": pk},
        "sk": {"S": sk},
        "doc_id": {"S": doc_id},
        "status": {"S": status},
        "author_id": {"S": author_id},
        "timestamp": {"S": timestamp},
    }

    if approver_id:
        item["approver_id"] = {"S": approver_id}

    if comment:
        item["comment"] = {"S": comment}

    try:
        dynamodb.put_item(
            TableName=TABLE_NAME,
            Item=item,
            ConditionExpression="attribute_not_exists(pk) AND attribute_not_exists(sk)",
        )
        logger.info(f"Audit log written for event_id={event_id}")

    except ClientError as e:
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            logger.warning(f"Duplicate event ignored: {event_id}")
            return   
        else:
            raise
