from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.entry import EntryType, EntryStatus, DetectedGoal


class EntryCreateRequest(BaseModel):
    """Request model for creating a new entry"""
    entry_type: EntryType
    content: str = Field(..., min_length=10, description="Entry content (session transcript or fresh thought)")
    title: Optional[str] = Field(None, max_length=100, description="Optional title, AI will generate if not provided")
    session_date: Optional[str] = Field(None, description="Session date in ISO format")
    coaching_relationship_id: Optional[str] = Field(None, description="Optional coaching relationship ID")
    input_method: Optional[str] = Field("paste", description="How content was input: 'paste' or 'upload'")
    file_name: Optional[str] = Field(None, description="Original filename if uploaded")


class EntryResponse(BaseModel):
    """Response model for entry operations"""
    id: str
    entry_type: str
    title: str
    client_user_id: str
    coach_user_id: Optional[str] = None
    coaching_relationship_id: Optional[str] = None
    session_date: Optional[str] = None
    status: str
    created_at: str
    updated_at: str
    completed_at: Optional[str] = None
    detected_goals: List[DetectedGoal] = Field(default_factory=list)
    has_insights: bool = Field(default=False, description="Whether entry has AI-generated insights")


class EntryDetailResponse(EntryResponse):
    """Detailed entry response with full insights"""
    content: Optional[str] = None
    transcript_content: Optional[str] = None
    celebrations: List[Dict[str, Any]] = Field(default_factory=list)
    intentions: List[Dict[str, Any]] = Field(default_factory=list)
    client_discoveries: List[Dict[str, Any]] = Field(default_factory=list)
    goal_progress: List[Dict[str, Any]] = Field(default_factory=list)
    coaching_presence: Optional[Dict[str, Any]] = None
    powerful_questions: List[Dict[str, Any]] = Field(default_factory=list)
    action_items: List[Dict[str, Any]] = Field(default_factory=list)
    emotional_shifts: List[Dict[str, Any]] = Field(default_factory=list)
    values_beliefs: List[Dict[str, Any]] = Field(default_factory=list)
    communication_patterns: Optional[Dict[str, Any]] = None


class EntryListResponse(BaseModel):
    """Response model for entry lists"""
    entries: List[EntryResponse]
    total_count: int
    has_more: bool
    freemium_limited: bool = Field(default=False, description="Whether results are limited due to freemium status")


class AcceptGoalsRequest(BaseModel):
    """Request to accept detected goals"""
    accepted_goal_indices: List[int] = Field(..., description="Indices of goals to accept")


class FreemiumStatusResponse(BaseModel):
    """Freemium status for entry creation"""
    has_coach: bool
    entries_count: int
    max_free_entries: int
    entries_remaining: int
    can_create_entries: bool
    can_access_insights: bool
    is_freemium: bool