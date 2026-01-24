import logging
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from src.dto.document import CreateDocumentRequest
from src.enums.document_status import DocumentStatus
from src.exceptions.app_exceptions import (
    BadRequestException,
    DocumentServiceError,
    ForbiddenException,
    InternalServerException,
    NotFoundException,
)
from src.models.document import Document
from src.repository.audit_repository import AuditRepo
from src.repository.document_repository import DocumentRepo
from src.repository.user_repository import UserRepo
from src.service.event_publisher_service import EventPublisher
from src.setup.api_settings import AppSettings

settings = AppSettings()
logger = logging.getLogger(__name__)


class DocumentService:
    def __init__(
        self,
        document_repo: DocumentRepo,
        audit_repo: AuditRepo,
        user_repo: UserRepo,
        event_publisher_service: EventPublisher,
    ):
        self.document_repo = document_repo
        self.audit_repo = audit_repo
        self.user_repo = user_repo
        self.event_publisher_service = event_publisher_service
        self.bucket_name = settings.S3_BUCKET_NAME

    async def create_document(self, user_ctx, doc_request: CreateDocumentRequest):

        if not user_ctx:
            raise BadRequestException("unauthorized or invalid user context")

        user_id = user_ctx.get("user_id")
        if not user_id:
            raise BadRequestException("missing user id in context")

        file_key = doc_request.file_key
        now = datetime.now()

        document = Document(
            id=doc_request.document_id,
            author_id=user_ctx["user_id"],
            status=DocumentStatus.PENDING,
            s3_path=f"s3://{self.bucket_name}/{file_key}",
            comment=None,
            created_at=now,
            updated_at=now,
        )

        try:
            await self.document_repo.create_document(document)
        except Exception as e:
            logger.exception("Failed to create document metadata")
            raise InternalServerException("Failed to create document") from e

        event_id = str(uuid.uuid4())

        event = {
            "event_id": event_id,
            "event_type": "DOCUMENT_CREATED",
            "payload": {
                "doc_id": doc_request.document_id,
                "author_id": user_ctx["user_id"],
                "status": "PENDING",
                "timestamp": now.isoformat(),
            },
        }

        await self.event_publisher_service.publish_status_updated(
            event=event, consumer="AUDIT"
        )

    async def get_all_document(
        self, user_ctx, status: Optional[str] = None
    ) -> List[Document]:

        if not user_ctx:
            raise BadRequestException("unauthorized or invalid user context")

        user_id = user_ctx.get("user_id")
        if not user_id:
            raise BadRequestException("missing user id in context")

        try:
            docs: List[Document] = await self.document_repo.get_documents(
                user_ctx, status
            )
            return docs

        except NotFoundException as e:
            logger.exception(f"error in the not found={e}")
            raise
        except Exception as e:
            raise DocumentServiceError(f"error occured in document service = {e}")

    async def update_status(
        self,
        user_ctx: dict,
        document_id: str,
        new_status: DocumentStatus,
        comment: Optional[str],
    ) -> Document:

        if not user_ctx:
            raise BadRequestException("invalid user context")

        if user_ctx.get("role") != "APPROVER":
            raise ForbiddenException("only approver can update status")

        try:
            doc = await self.document_repo.get_by_id(document_id)
        except NotFoundException:
            raise
        except Exception as e:
            raise DocumentServiceError(f"failed loading document: {e}")

        old_status = doc.status

        # valid transitions
        if old_status == DocumentStatus.PENDING:
            if new_status not in (DocumentStatus.APPROVED, DocumentStatus.REJECTED):
                raise BadRequestException("cannot move from PENDING to given status")

        if old_status in (DocumentStatus.APPROVED, DocumentStatus.REJECTED):
            if new_status == old_status:
                raise BadRequestException(f"your status is already {new_status.value} ")

        now = datetime.now(timezone.utc)

        try:
            updated = await self.document_repo.update_status(
                doc=doc, new_status=new_status, comment=comment, now=now
            )
            author = await self.user_repo.find_by_id(doc.author_id)
        except InternalServerException:
            raise
        except Exception as e:
            raise DocumentServiceError(f"failed updating status: {e}")

        event_id = str(uuid.uuid4())

        event = {
            "event_id": event_id,
            "event_type": "DOCUMENT_STATUS_UPDATED",
            "payload": {
                "doc_id": document_id,
                "old_status": old_status,
                "new_status": new_status,
                "author_id": doc.author_id,
                "approver_id": user_ctx["user_id"],
                "author_email": author.email,
                "comment": comment,
                "timestamp": now.isoformat(),
            },
        }

        # Publish for audit
        await self.event_publisher_service.publish_status_updated(
            event=event, consumer="AUDIT"
        )

        # Publish for noti
        await self.event_publisher_service.publish_status_updated(
            event=event, consumer="NOTIFY"
        )

        return updated
