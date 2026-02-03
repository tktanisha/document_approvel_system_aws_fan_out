from datetime import datetime
from typing import Optional,List

from enums.document_status import DocumentStatus
from pydantic import BaseModel


# class PresignRequest(BaseModel):
#     filename: str
#     content_type: str


# class PresignResponse(BaseModel):
#     document_id: str
#     upload_url: str
#     file_key: str


class MultipartInitiateRequest(BaseModel):
    filename: str
    content_type: str


class MultipartInitiateResponse(BaseModel):
    document_id: str
    upload_id: str
    file_key: str


class MultipartPresignPartRequest(BaseModel):
    upload_id: str
    file_key: str
    part_number: int


class MultipartPresignPartResponse(BaseModel):
    upload_url: str


class MultipartCompletePart(BaseModel):
    part_number: int
    etag: str


class MultipartCompleteRequest(BaseModel):
    upload_id: str
    file_key: str
    parts: List[MultipartCompletePart]



class DocumentResponse(BaseModel):
    document_id: str
    author_id: str
    status: DocumentStatus
    s3_path: str
    comment: Optional[str]
    created_at: datetime
    updated_at: datetime


class CreateDocumentRequest(BaseModel):
    document_id: str
    file_key: str


class UpdateStatusRequest(BaseModel):
    status: DocumentStatus
    comment: Optional[str] = None
