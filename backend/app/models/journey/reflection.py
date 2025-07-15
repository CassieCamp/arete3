"""
Journey System Reflection Models

This module contains models for reflection sources and processing events.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import Field

from .base import ProcessableDocument, BaseJourneyDocument
from .enums import CategoryType, DocumentType, ProcessingStatus


class ReflectionSource(ProcessableDocument):
    """Model for reflection sources that can be processed into insights"""
    
    # Core identification
    title: str = Field(..., description="Title or name of the reflection source")
    description: Optional[str] = Field(default=None, description="Optional description of the source")
    
    # Content and metadata
    content: Optional[str] = Field(default=None, description="Raw text content of the reflection")
    file_path: Optional[str] = Field(default=None, description="Path to uploaded file if applicable")
    file_name: Optional[str] = Field(default=None, description="Original filename if uploaded")
    file_size: Optional[int] = Field(default=None, description="File size in bytes")
    document_type: Optional[DocumentType] = Field(default=None, description="Type of document")
    
    # Categorization
    categories: List[CategoryType] = Field(default_factory=list, description="Categories assigned to this reflection")
    tags: List[str] = Field(default_factory=list, description="User-defined tags")
    
    # Processing configuration
    auto_process: bool = Field(default=True, description="Whether to automatically process this source")
    processing_priority: int = Field(default=0, description="Processing priority (higher = more urgent)")
    
    # Relationships
    insight_ids: List[str] = Field(default_factory=list, description="IDs of insights generated from this source")
    
    # Analytics
    word_count: Optional[int] = Field(default=None, description="Word count of the content")
    reading_time_minutes: Optional[int] = Field(default=None, description="Estimated reading time")
    
    class Config:
        """Pydantic configuration"""
        json_encoders = {datetime: lambda v: v.isoformat()}


class ProcessingEvent(BaseJourneyDocument):
    """Model for tracking processing events and history"""
    
    # Event identification
    event_type: str = Field(..., description="Type of processing event")
    event_status: ProcessingStatus = Field(..., description="Status of the event")
    
    # Related entities
    source_id: str = Field(..., description="ID of the reflection source being processed")
    user_id: str = Field(..., description="Clerk user ID of the owner")
    
    # Event details
    message: Optional[str] = Field(default=None, description="Human-readable event message")
    error_details: Optional[str] = Field(default=None, description="Detailed error information if failed")
    
    # Processing metadata
    processing_duration_ms: Optional[int] = Field(default=None, description="Processing duration in milliseconds")
    tokens_used: Optional[int] = Field(default=None, description="AI tokens consumed during processing")
    model_version: Optional[str] = Field(default=None, description="AI model version used")
    
    # Additional context
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional event metadata")
    
    # Timestamps
    started_at: Optional[datetime] = Field(default=None, description="When the event started")
    completed_at: Optional[datetime] = Field(default=None, description="When the event completed")
    
    class Config:
        """Pydantic configuration"""
        json_encoders = {datetime: lambda v: v.isoformat()}