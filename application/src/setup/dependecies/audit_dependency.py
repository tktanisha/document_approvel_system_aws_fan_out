from typing import Annotated

from fastapi import Depends
from src.repository.audit_repository import AuditRepo
from src.service.audit_service import AuditService
from src.setup.db_connection import get_dynamodb


def get_audit_repo(dynamodb=Depends(get_dynamodb)) -> AuditRepo:
    return AuditRepo(dynamodb=dynamodb)


def get_audit_service(
    audit_repo: Annotated[AuditRepo, Depends(get_audit_repo)]
) -> AuditService:
    return AuditService(audit_repo=audit_repo)
