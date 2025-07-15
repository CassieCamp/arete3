from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.models.journey.enums import ProcessingStatus

class UserOwnedDocument(BaseModel):
    """Base model for documents owned by a user."""
    id: Optional[str] = Field(default=None, alias="_id", description="Unique identifier")
    user_id: str = Field(..., description="Clerk user ID of the owner")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ProcessableDocument(UserOwnedDocument):
    """Base model for documents that undergo a processing workflow."""
    processing_status: ProcessingStatus = Field(default=ProcessingStatus.PENDING, description="Current processing status")
    processing_errors: Optional[str] = Field(default=None, description="Any errors from processing")