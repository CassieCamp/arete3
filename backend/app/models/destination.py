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
    percentage: Optional[int] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Destination(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    user_id: str  # Foreign key to User
    
    # RENAMED: Core fields
    destination_statement: str  # Renamed from goal_statement
    success_vision: str  # Maintained
    
    # NEW: Three Big Ideas categorization
    is_big_idea: bool = False  # Default false for existing goals
    big_idea_rank: Optional[int] = None  # 1-3 for ranking, null for regular destinations
    
    # ENHANCED: Progress tracking
    progress_percentage: Optional[int] = None  # Maintain existing
    progress_emoji: str = "😐"  # Current emotional state
    progress_notes: Optional[str] = None  # Optional qualitative notes
    progress_history: List[ProgressEntry] = Field(default_factory=list)
    
    # NEW: Enhanced categorization
    priority: str = "medium"  # "high", "medium", "low"
    category: str = "personal"  # "personal", "professional", "health", "relationships"
    
    # NEW: AI and source tracking
    ai_suggested: bool = False  # false for existing goals
    source_documents: List[str] = Field(default_factory=list)  # Document IDs that inspired this destination
    source_entries: List[str] = Field(default_factory=list)  # Entry IDs that inspired this destination
    
    # EXISTING: Status and metadata (maintain all)
    status: str = "active"  # active, completed, paused
    tags: List[str] = Field(default_factory=list)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Legacy fields for backward compatibility (will be deprecated)
    goal_statement: Optional[str] = None  # Maps to destination_statement
    title: Optional[str] = None  # Maps to destination_statement
    description: Optional[str] = None  # Maps to success_vision
    target_date: Optional[datetime] = None  # Deprecated
    completion_date: Optional[datetime] = None  # Deprecated
    notes: Optional[str] = None  # Maps to progress_notes