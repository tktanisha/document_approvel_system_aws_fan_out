# events.py

import logging
from email_service import send_email

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handle_event(event_type: str, payload: dict):
    if event_type == "DOCUMENT_STATUS_UPDATED":
        handle_status_updated(payload)
    else:
        logger.info(f"Ignoring unknown event_type: {event_type}")


def handle_status_updated(payload: dict):
    author_email = payload.get("author_email")
    doc_id = payload.get("doc_id")
    new_status = payload.get("new_status")
    comment = payload.get("comment")

    subject = f"Your document {doc_id} was {new_status}"

    body = f"""
    Hello,

    Your document with ID {doc_id} has been {new_status}.

    Comment from approver:
    {comment or "No comment"}

    Regards,
    Document System
    """

    send_email(author_email,subject, body)

