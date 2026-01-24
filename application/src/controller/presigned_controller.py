from fastapi import APIRouter, Depends, Request, status
from src.dto.document import PresignRequest, PresignResponse
from src.helpers.api_paths import ApiPaths
from src.helpers.auth_helper import AuthHelper
from src.helpers.success_response import write_success_response
from src.service.presigned_service import PresignedService

router = APIRouter(
    tags=["Presigned url"], dependencies=[Depends(AuthHelper.verify_jwt)]
)


@router.post(ApiPaths.PRESIGNED_URL, response_model=PresignResponse)
async def generate_presigned_url(
    request: Request,
    payload: PresignRequest,
    presigned_service: PresignedService = Depends(PresignedService),
):
    user_ctx = request.state.user
    print(user_ctx)

    presigned_response: PresignResponse = (
        await presigned_service.generate_presigned_url(presigned_request=payload)
    )

    return write_success_response(
        status_code=status.HTTP_200_OK,
        data=presigned_response.model_dump(),
        message="Pre-signed URL generated successfully",
    )
