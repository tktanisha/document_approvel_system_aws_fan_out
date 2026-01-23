
from fastapi import Depends
from typing import Annotated
from src.repository.audit_repository import AuditRepo
from src.setup.db_connection import get_dynamodb
from src.service.audit_service import AuditService


def get_audit_repo(
        dynamodb = Depends(get_dynamodb)
) -> AuditRepo:
    return AuditRepo(dynamodb = dynamodb) 


def get_audit_service(
        audit_repo: Annotated[AuditRepo , Depends(get_audit_repo)]
) -> AuditService:
    return AuditService(audit_repo=audit_repo) 




