from datetime import datetime
from typing import Optional

from enums.document_status import DocumentStatus
from pydantic import BaseModel


class Document(BaseModel):
    id: str
    author_id: str
    status: DocumentStatus
    s3_path: str
    comment: Optional[str] = None
    created_at: datetime
    updated_at: datetime
