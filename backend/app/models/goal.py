from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List
from bson import ObjectId


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


class ProgressEntry(BaseModel):
    """Represents a single progress update with emoji and optional notes"""
    emoji: str
    notes: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Goal(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    user_id: str  # Foreign key to User
    
    # Core human-centered fields
    goal_statement: str  # Simple "what you want to work on"
    success_vision: str  # "How you'll know it's working"
    progress_emoji: str = "😐"  # Current emotional state
    progress_notes: Optional[str] = None  # Optional qualitative notes
    
    # Progress history for tracking emotional journey
    progress_history: List[ProgressEntry] = Field(default_factory=list)
    
    # AI and document integration
    ai_suggested: bool = False  # Flag for AI-generated goals
    source_documents: List[str] = Field(default_factory=list)  # Document IDs that inspired this goal
    
    # Simplified metadata
    status: str = "active"  # active, completed, paused
    tags: List[str] = Field(default_factory=list)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Legacy fields for backward compatibility (will be deprecated)
    title: Optional[str] = None  # Maps to goal_statement
    description: Optional[str] = None  # Maps to success_vision
    priority: Optional[str] = None  # Deprecated
    target_date: Optional[datetime] = None  # Deprecated
    completion_date: Optional[datetime] = None  # Deprecated
    progress_percentage: Optional[int] = None  # Deprecated
    notes: Optional[str] = None  # Maps to progress_notes