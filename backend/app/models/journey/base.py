"""
Journey System Base Classes

This module contains base classes and common utilities for the Journey System models.
"""

from typing import Optional, Any, Dict
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom ObjectId class for Pydantic compatibility"""
    
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


class BaseJourneyDocument(BaseModel):
    """Base class for all Journey System documents"""
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    def dict(self, **kwargs):
        """Override dict method to handle ObjectId serialization"""
        data = super().dict(**kwargs)
        if "_id" in data and data["_id"]:
            data["_id"] = str(data["_id"])
        return data


class UserOwnedDocument(BaseJourneyDocument):
    """Base class for documents owned by a specific user"""
    
    user_id: str = Field(..., description="Clerk user ID of the document owner")
    
    class Config:
        """Pydantic configuration"""
        json_encoders = {ObjectId: str}


class ProcessableDocument(UserOwnedDocument):
    """Base class for documents that can be processed"""
    
    processing_status: str = Field(default="pending", description="Current processing status")
    processing_started_at: Optional[datetime] = Field(default=None, description="When processing started")
    processing_completed_at: Optional[datetime] = Field(default=None, description="When processing completed")
    processing_error: Optional[str] = Field(default=None, description="Error message if processing failed")
    processing_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional processing metadata")
    
    def mark_processing_started(self):
        """Mark the document as processing started"""
        self.processing_status = "processing"
        self.processing_started_at = datetime.utcnow()
        self.processing_error = None
        self.updated_at = datetime.utcnow()
    
    def mark_processing_completed(self):
        """Mark the document as processing completed"""
        self.processing_status = "completed"
        self.processing_completed_at = datetime.utcnow()
        self.processing_error = None
        self.updated_at = datetime.utcnow()
    
    def mark_processing_failed(self, error_message: str):
        """Mark the document as processing failed"""
        self.processing_status = "failed"
        self.processing_error = error_message
        self.updated_at = datetime.utcnow()