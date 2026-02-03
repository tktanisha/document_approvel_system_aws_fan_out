import logging
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from dto.document import CreateDocumentRequest
from enums.document_status import DocumentStatus
from enums.user_role import Role
from exceptions.app_exceptions import (
    BadRequestException,
    DocumentServiceError,
    ForbiddenException,
    InternalServerException,
    NotFoundException,
)
from helpers.common import Common
from models.document import Document
from repository.audit_repository import AuditRepo
from repository.document_repository import DocumentRepo
from repository.user_repository import UserRepo
from service.event_publisher_service import EventPublisher
from setup.api_settings import AppSettings

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
            raise BadRequestException(Common.UNAUTHORIZED_OR_INVALID_USER_CONTEXT)

        user_id = user_ctx.get("user_id")
        if not user_id:
            raise BadRequestException(Common.MISSING_USER_ID_IN_CONTEXT)

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
            logger.exception(Common.FAILED_CREATE_DOCUMENT_METADATA_LOG)
            raise InternalServerException(Common.FAILED_CREATE_DOCUMENT) from e

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
            raise BadRequestException(Common.UNAUTHORIZED_OR_INVALID_USER_CONTEXT)

        user_id = user_ctx.get("user_id")
        if not user_id:
            raise BadRequestException(Common.MISSING_USER_ID_IN_CONTEXT)

        try:
            docs: List[Document] = await self.document_repo.get_documents(
                user_ctx, status
            )
            return docs

        except NotFoundException as e:
            logger.exception(f"error in the not found={e}")
            raise
        except Exception as e:
            raise DocumentServiceError(
                Common.DOCUMENT_SERVICE_FAILED.format(error=e)
            )

    async def update_status(
        self,
        user_ctx: dict,
        document_id: str,
        new_status: DocumentStatus,
        comment: Optional[str],
    ) -> Document:

        if not user_ctx:
            raise BadRequestException(Common.INVALID_USER_CONTEXT)

        if user_ctx.get("role") != Role.APPROVER.value:
            raise ForbiddenException(Common.ONLY_APPROVER_CAN_UPDATE_STATUS)

        try:
            doc = await self.document_repo.get_by_id(document_id)
        except NotFoundException:
            raise
        except Exception as e:
            raise DocumentServiceError(
                Common.FAILED_LOADING_DOCUMENT.format(error=e)
            )

        old_status = doc.status

        if old_status == DocumentStatus.PENDING:
            if new_status not in (DocumentStatus.APPROVED, DocumentStatus.REJECTED):
                raise BadRequestException(
                    f"{Common.CANNOT_MOVE_FROM_PENDING} {new_status}"
                )

        if old_status in (DocumentStatus.APPROVED, DocumentStatus.REJECTED):
            if new_status == old_status:
                raise BadRequestException(
                    Common.STATUS_ALREADY_VALUE.format(status=new_status.value)
                )

        now = datetime.now(timezone.utc)

        try:
            updated = await self.document_repo.update_status(
                doc=doc, new_status=new_status, comment=comment, now=now
            )
            author = await self.user_repo.find_by_id(doc.author_id)
        except InternalServerException:
            raise
        except Exception as e:
            raise DocumentServiceError(
                Common.FAILED_UPDATING_STATUS.format(error=e)
            )

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

        await self.event_publisher_service.publish_status_updated(
            event=event, consumer="AUDIT"
        )

        await self.event_publisher_service.publish_status_updated(
            event=event, consumer="NOTIFY"
        )

        return updated
