from dto.document import PresignRequest, PresignResponse
from fastapi import APIRouter, Depends, Request, status
from helpers.api_paths import ApiPaths
from helpers.auth_helper import AuthHelper
from helpers.common import Common
from helpers.success_response import write_success_response
from service.presigned_service import PresignedService

router = APIRouter(
    tags=["Presigned url"], dependencies=[Depends(AuthHelper.verify_jwt)]
)


@router.post(ApiPaths.PRESIGNED_URL, response_model=PresignResponse)
async def generate_presigned_url(
    payload: PresignRequest,
    presigned_service: PresignedService = Depends(PresignedService),
):

    presigned_response: PresignResponse = (
        await presigned_service.generate_presigned_url(presigned_request=payload)
    )

    return write_success_response(
        status_code=status.HTTP_200_OK,
        data=presigned_response.model_dump(),
        message=Common.PRESIGNED_URL_GENERATE_SUCCESS,
    )
