from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from helpers.api_paths import ApiPaths
from helpers.auth_helper import AuthHelper
from helpers.common import Common
from helpers.success_response import write_success_response
from service.audit_service import AuditService
from setup.dependecies.audit_dependency import get_audit_service

router = APIRouter(tags=["Audits"], dependencies=[Depends(AuthHelper.verify_jwt)])


@router.get(ApiPaths.GET_AUDIT_LOGS)
async def get_audit_logs(
    request: Request,
    audit_service: Annotated[AuditService, Depends(get_audit_service)],
):
    user_ctx = request.state.user
    logs = await audit_service.get_all_audit_logs(user_ctx=user_ctx)
    return write_success_response(
        status_code=status.HTTP_200_OK,
        data=[
            {
                **l.model_dump(exclude={"timestamp"}),
                "created_at": l.timestamp.isoformat(),
            }
            for l in logs
        ],
          message=Common.AUDIT_LOGS_FETCH_SUCCESS,
    )
