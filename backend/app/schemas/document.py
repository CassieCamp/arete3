from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from app.models.document import DocumentCategory, DocumentType


class DocumentResponse(BaseModel):
    id: str
    user_id: str
    clerk_user_id: str
    file_name: str
    file_type: DocumentType
    file_size: int
    s3_url: Optional[str] = None
    local_path: Optional[str] = None
    extracted_text: Optional[str] = None
    category: DocumentCategory
    tags: List[str] = []
    description: Optional[str] = None
    is_processed: bool
    processing_error: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True