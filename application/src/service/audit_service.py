from typing import List
from helpers.common import Common
from enums.user_role import Role
from exceptions.app_exceptions import AuditServiceError, BadRequestException
from models.audit_log import AuditLog
from repository.audit_repository import AuditRepo


class AuditService:
    def __init__(self, audit_repo: AuditRepo):
        self.audit_repo = audit_repo

    async def get_all_audit_logs(self, user_ctx: dict) -> List[AuditLog]:
        if not user_ctx:
            raise BadRequestException(Common.UNAUTHORIZED_OR_INVALID_USER_CONTEXT)

        role = user_ctx.get("role")
        user_id = user_ctx.get("user_id")

        if not role:
            raise BadRequestException(Common.MISSING_USER_ROLE_IN_CONTEXT)

        try:
            if role == Role.AUTHOR.value:
                if not user_id:
                    raise BadRequestException(Common.MISSING_USER_ID_FOR_AUTHOR)
                return await self.audit_repo.get_all_logs(user_id=user_id)

            elif role == Role.APPROVER.value:
                return await self.audit_repo.get_all_logs()

            else:
                raise BadRequestException(Common.ROLE_NOT_PERMITTED_VIEW_LOGS)

        except Exception as e:
            raise AuditServiceError(Common.FAILED_FETCH_AUDIT_LOGS.format(error=e))
