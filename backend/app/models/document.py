from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from bson import ObjectId
from datetime import datetime
from enum import Enum


class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        from pydantic_core import core_schema
        return core_schema.no_info_after_validator_function(
            cls.validate,
            core_schema.str_schema(),
            serialization=core_schema.to_string_ser_schema(),
        )

    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str):
            if ObjectId.is_valid(v):
                return ObjectId(v)
        raise ValueError("Invalid ObjectId")


class DocumentCategory(str, Enum):
    """Document categories for organization and context"""
    RESUME = "resume"
    PERFORMANCE_REVIEW = "performance_review"
    GOALS_OBJECTIVES = "goals_objectives"
    FEEDBACK = "feedback"
    ASSESSMENT = "assessment"
    DEVELOPMENT_PLAN = "development_plan"
    PROJECT_DOCUMENTATION = "project_documentation"
    MEETING_NOTES = "meeting_notes"
    OTHER = "other"


class DocumentType(str, Enum):
    """Supported document file types"""
    PDF = "pdf"
    DOCX = "docx"
    DOC = "doc"
    TXT = "txt"
    RTF = "rtf"
    ODT = "odt"


class Document(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    user_id: str  # Foreign key to User (MongoDB ObjectId as string)
    clerk_user_id: str  # Clerk user ID for direct integration
    file_name: str  # Original filename
    file_type: DocumentType  # File extension/type
    file_size: int  # File size in bytes
    s3_url: Optional[str] = None  # S3 storage URL (when cloud storage is implemented)
    local_path: Optional[str] = None  # Local file path (for development/local storage)
    extracted_text: Optional[str] = None  # Extracted text content from the document
    category: DocumentCategory = DocumentCategory.OTHER  # Document category
    tags: List[str] = Field(default_factory=list)  # User-defined tags for organization
    description: Optional[str] = None  # User-provided description
    is_processed: bool = False  # Whether text extraction has been completed
    processing_error: Optional[str] = None  # Error message if processing failed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    def __str__(self) -> str:
        return f"Document(file_name='{self.file_name}', category='{self.category}', user_id='{self.user_id}')"