from typing import Annotated

from fastapi import Depends
from repository.document_repository import DocumentRepo
from repository.user_repository import UserRepo
from service.document_service import DocumentService
from service.event_publisher_service import EventPublisher
from setup.db_connection import get_dynamodb
from setup.dependecies.audit_dependency import get_audit_repo
from setup.dependecies.auth_dependency import get_user_repo
from setup.dependecies.event_pub_dependency import get_event_pub_service


def get_document_repo(dynamodb=Depends(get_dynamodb)) -> DocumentRepo:
    return DocumentRepo(dynamodb=dynamodb)


def get_document_service(
    document_repo: Annotated[DocumentRepo, Depends(get_document_repo)],
    audit_repo: Annotated[DocumentRepo, Depends(get_audit_repo)],
    event_publisher_service: Annotated[EventPublisher, Depends(get_event_pub_service)],
    user_repo: Annotated[UserRepo, Depends(get_user_repo)],
) -> DocumentService:
    return DocumentService(
        document_repo=document_repo,
        audit_repo=audit_repo,
        user_repo=user_repo,
        event_publisher_service=event_publisher_service,
    )
