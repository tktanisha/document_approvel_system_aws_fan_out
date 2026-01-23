from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from src.enums.document_status import DocumentStatus

class Document(BaseModel):
    id:str
    author_id: str
    status: DocumentStatus
    s3_path: str
    comment: Optional[str] = None
    created_at: datetime
    updated_at: datetime
