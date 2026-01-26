from datetime import datetime
from typing import Optional

from enums.document_status import DocumentStatus
from pydantic import BaseModel


class AuditLog(BaseModel):
    doc_id: str
    approver_id: Optional[str] = None
    comment: Optional[str] = None
    status: DocumentStatus
    author_id: str
    timestamp: datetime
