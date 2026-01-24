from typing import List

from src.enums.user_role import Role
from src.exceptions.app_exceptions import (
    AuditServiceError,
    BadRequestException,
)
from src.models.audit_log import AuditLog
from src.repository.audit_repository import AuditRepo


class AuditService:
    def __init__(self, audit_repo: AuditRepo):
        self.audit_repo = audit_repo

    async def get_all_audit_logs(self, user_ctx: dict) -> List[AuditLog]:
        if not user_ctx:
            raise BadRequestException("unauthorized or invalid user context")

        role = user_ctx.get("role")
        user_id = user_ctx.get("user_id")

        if not role:
            raise BadRequestException("missing user role in context")

        try:
            if role == Role.AUTHOR.value:
                if not user_id:
                    raise BadRequestException("missing user id for author")
                return await self.audit_repo.get_all_logs(user_id=user_id)

            elif role == Role.APPROVER.value:
                return await self.audit_repo.get_all_logs()

            else:
                raise BadRequestException("role not permitted to view logs")

        except Exception as e:
            raise AuditServiceError(f"failed to fetch audit logs == {e}")
