from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from enums.document_status import DocumentStatus


class PresignRequest(BaseModel):
    filename: str
    content_type: str


class PresignResponse(BaseModel):
    document_id: str
    upload_url: str
    file_key: str


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
