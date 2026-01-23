
import boto3
import logging
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ses = boto3.client("ses")

FROM_EMAIL = os.environ.get("FROM_EMAIL")


def send_email(to_email: str, subject: str, body: str):
    print("email==",to_email)
    if not to_email:
        logger.warning("No email provided, skipping notification")
        return

    response = ses.send_email(
        Source=FROM_EMAIL,
        Destination={
            "ToAddresses": [to_email]
        },
        Message={
            "Subject": {"Data": subject},
            "Body": {
                "Text": {"Data": body}
            }
        }
    )

    logger.info(f"Email sent to {to_email}, MessageId={response['MessageId']}")
