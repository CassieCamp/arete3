from datetime import datetime
from typing import Optional, List, Dict
from pydantic import Field, BaseModel
from app.models.journey.base import ProcessableDocument
from app.models.journey.enums import ProcessingStatus, DocumentType, CategoryType

class DocumentAnalysis(BaseModel):
    """AI analysis results for a processed document."""
    summary: str = Field(..., description="AI-generated summary of the document content")
    key_themes: List[str] = Field(default_factory=list, description="Main themes identified in the document")
    sentiment: str = Field(..., description="Overall sentiment of the document (e.g., positive, negative, neutral)")
    sentiment_score: float = Field(..., description="Numerical sentiment score, typically between -1.0 and 1.0")
    entities: Dict[str, List[str]] = Field(default_factory=dict, description="Named entities extracted from the document, categorized by type (e.g., people, places, organizations)")

class ReflectionSource(ProcessableDocument):
    """Complete reflection source model for MongoDB persistence"""
    title: str = Field(..., description="Title or name of the reflection source")
    description: Optional[str] = Field(default=None, description="Optional description")
    content: str = Field(..., description="Extracted text content")
    original_filename: Optional[str] = Field(default=None, description="Original uploaded filename")
    file_path: Optional[str] = Field(default=None, description="Path to stored file")
    file_size: Optional[int] = Field(default=None, description="File size in bytes")
    content_type: Optional[str] = Field(default=None, description="MIME type of uploaded file")
    document_type: Optional[DocumentType] = Field(default=None, description="Type of document")
    document_analysis: Optional[DocumentAnalysis] = Field(default=None, description="AI analysis of document")
    categories: List[CategoryType] = Field(default_factory=list, description="Assigned categories")
    tags: List[str] = Field(default_factory=list, description="User-defined tags")
    processing_status: ProcessingStatus = Field(default=ProcessingStatus.PENDING)
    insight_ids: List[str] = Field(default_factory=list, description="IDs of generated insights")
    word_count: Optional[int] = Field(default=None, description="Word count of content")
    character_count: Optional[int] = Field(default=None, description="Character count of content")
    text_extraction_completed_at: Optional[datetime] = Field(default=None)
    ai_processing_completed_at: Optional[datetime] = Field(default=None)

    class Config:
        collection_name = "journey_reflections"