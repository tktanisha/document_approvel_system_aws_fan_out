from fastapi import status,APIRouter,Depends,Request,Query
from src.helpers.api_paths import ApiPaths
from typing import Annotated,Optional
from enum import Enum
from src.service.document_service import DocumentService
from src.setup.dependecies.document_dependency import get_document_service
from src.dto.document import CreateDocumentRequest, UpdateStatusRequest
from src.helpers.success_response import write_success_response
from src.helpers.auth_helper import AuthHelper
from src.service.presigned_service import PresignedService

router = APIRouter(tags=["Documents"] , dependencies=[Depends(AuthHelper.verify_jwt)])

class StatusName(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


@router.get(ApiPaths.GET_ALL_DOCUMENTS)
async def get_all_document(
    request: Request, 
    document_service: Annotated[DocumentService, Depends(get_document_service)],
    presigned_service: PresignedService = Depends(PresignedService),
    doc_status: Optional[StatusName] = Query(default=None, alias="status"), 
):
    user_ctx = request.state.user
    
    status_value = doc_status.value if doc_status else None

    documents = await document_service.get_all_document(user_ctx, status=status_value)
    result = []

    for doc in documents:
        # Extract "documents/<id>/filename"
        file_key = doc.s3_path.replace("s3://my-doc-approval-bucket/", "")
        
        view_url = await presigned_service.generate_presigned_get_url(file_key)

        result.append({
            **doc.model_dump(exclude={"created_at", "updated_at","s3_path"}),
            "created_at": doc.created_at.isoformat(),
            "updated_at": doc.updated_at.isoformat(),
            "doc_url": view_url      
        })

    return write_success_response(
        status_code=status.HTTP_200_OK,
        data=result,
        message="Documents fetched successfully"
    )


@router.post(ApiPaths.UPLOAD_DOCUMENT)
async def create_document(
    request: Request,
    payload: CreateDocumentRequest,
    document_service: Annotated[DocumentService, Depends(get_document_service)]
):
    user_ctx = request.state.user

    await document_service.create_document(
        user_ctx=user_ctx,
        doc_request= payload
    )

    return write_success_response(
        status_code=status.HTTP_201_CREATED,
        message="Document created successfully"
    )


@router.patch(ApiPaths.UPDATE_DOCUMENT_STATUS)
async def update_document_status(
    request: Request,
    document_id: str,
    body: UpdateStatusRequest,
    document_service: Annotated[DocumentService, Depends(get_document_service)]
):
    user_ctx = request.state.user
    doc = await document_service.update_status(user_ctx=user_ctx, document_id=document_id, new_status=body.status, comment=body.comment)
    return write_success_response(
        status_code=status.HTTP_200_OK,
        data={**doc.model_dump(exclude={"created_at", "updated_at"}),
            "created_at": doc.created_at.isoformat(),
            "updated_at": doc.updated_at.isoformat()
        },
        message="status updated successfully"
    )
