from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class ProgressEntryResponse(BaseModel):
    """Response schema for progress entries"""
    emoji: str
    notes: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True


class GoalResponse(BaseModel):
    """Response schema for goals with human-centered structure"""
    id: str
    user_id: str
    
    # Core human-centered fields
    goal_statement: str
    success_vision: str
    progress_emoji: str
    progress_notes: Optional[str] = None
    
    # Progress history
    progress_history: List[ProgressEntryResponse] = []
    
    # AI and document integration
    ai_suggested: bool = False
    source_documents: List[str] = []
    
    # Metadata
    status: str
    tags: List[str] = []
    
    # Timestamps
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GoalCreateRequest(BaseModel):
    """Request schema for creating goals"""
    goal_statement: str
    success_vision: str
    progress_emoji: Optional[str] = "😐"
    progress_notes: Optional[str] = None
    ai_suggested: Optional[bool] = False
    source_documents: Optional[List[str]] = []
    tags: Optional[List[str]] = []


class GoalUpdateRequest(BaseModel):
    """Request schema for updating goals"""
    goal_statement: Optional[str] = None
    success_vision: Optional[str] = None
    progress_emoji: Optional[str] = None
    progress_notes: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None


class ProgressUpdateRequest(BaseModel):
    """Request schema for updating progress with emoji"""
    emoji: str
    notes: Optional[str] = None


class GoalSuggestionResponse(BaseModel):
    """Response schema for AI-generated goal suggestions"""
    goal_statement: str
    success_vision: str
    source_documents: List[str] = []


class SuccessVisionSuggestionResponse(BaseModel):
    """Response schema for success vision suggestions"""
    suggestions: List[str]