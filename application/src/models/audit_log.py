from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from src.enums.document_status import DocumentStatus


class AuditLog(BaseModel):
    doc_id: str
    approver_id: Optional[str] = None
    comment: Optional[str] = None
    status: DocumentStatus
    author_id: str
    timestamp: datetime
