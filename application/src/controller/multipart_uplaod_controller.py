from fastapi import APIRouter, Depends, status
from helpers.auth_helper import AuthHelper
from helpers.success_response import write_success_response
from service.multipart_uplaod_service import MultipartPresignedService
from dto.document import (
    MultipartInitiateRequest,
    MultipartPresignPartRequest,
    MultipartCompleteRequest,
)

router = APIRouter(
    tags=["Multipart Upload"],
    dependencies=[Depends(AuthHelper.verify_jwt)]
)


# 1️⃣ Initiate multipart upload
@router.post("/documents/multipart/initiate")
async def initiate_multipart_upload(
    payload: MultipartInitiateRequest,
    service: MultipartPresignedService = Depends(MultipartPresignedService),
):
    result = await service.initiate_multipart_upload(
        filename=payload.filename,
        content_type=payload.content_type,
    )

    return write_success_response(
        status_code=status.HTTP_200_OK,
        data=result,
        message="Multipart upload initiated",
    )


# 2️⃣ Get presigned URL for a part
@router.post("/documents/multipart/presign-part")
async def presign_part(
    payload: MultipartPresignPartRequest,
    service: MultipartPresignedService = Depends(MultipartPresignedService),
):
    upload_url = await service.generate_presigned_part_url(
        upload_id=payload.upload_id,
        file_key=payload.file_key,
        part_number=payload.part_number,
    )

    return write_success_response(
        status_code=status.HTTP_200_OK,
        data={"upload_url": upload_url},
        message="Presigned part URL generated",
    )


# 3️⃣ Complete multipart upload
@router.post("/documents/multipart/complete")
async def complete_multipart_upload(
    payload: MultipartCompleteRequest,
    service: MultipartPresignedService = Depends(MultipartPresignedService),
):
    await service.complete_multipart_upload(
        upload_id=payload.upload_id,
        file_key=payload.file_key,
        parts=payload.parts,
    )

    return write_success_response(
        status_code=status.HTTP_200_OK,
        data={},
        message="Multipart upload completed successfully",
    )


# 4️⃣ Abort multipart upload
@router.post("/documents/multipart/abort")
async def abort_multipart_upload(
    upload_id: str,
    file_key: str,
    service: MultipartPresignedService = Depends(MultipartPresignedService),
):
    await service.abort_multipart_upload(upload_id, file_key)

    return write_success_response(
        status_code=status.HTTP_200_OK,
        data={},
        message="Multipart upload aborted",
    )
