from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class SessionInsightCreateRequest(BaseModel):
    coaching_relationship_id: str
    session_date: Optional[str] = None  # ISO format
    session_title: Optional[str] = None
    transcript_text: Optional[str] = None  # For direct text input


class UnpairedSessionInsightCreateRequest(BaseModel):
    session_date: Optional[str] = None
    session_title: Optional[str] = None
    transcript_text: str


class ShareInsightRequest(BaseModel):
    coach_user_id: str
    permissions: Dict[str, bool] = {
        "view": True,
        "comment": False,
        "export": False
    }


class SessionInsightResponse(BaseModel):
    id: str
    coaching_relationship_id: Optional[str] = None
    client_user_id: str
    coach_user_id: Optional[str] = None
    is_unpaired: bool = False
    session_date: Optional[str] = None
    session_title: Optional[str] = None
    session_summary: str
    key_themes: List[str]
    overall_session_quality: str
    status: str
    created_at: str
    completed_at: Optional[str] = None
    
    # Simplified insight counts for list view
    celebration_count: int = 0
    intention_count: int = 0
    discovery_count: int = 0
    action_item_count: int = 0


class SessionInsightDetailResponse(SessionInsightResponse):
    """Extended response with full insight details"""
    celebration: Optional[Dict[str, Any]] = None
    intention: Optional[Dict[str, Any]] = None
    client_discoveries: List[Dict[str, Any]] = []
    goal_progress: List[Dict[str, Any]] = []
    coaching_presence: Optional[Dict[str, Any]] = None
    powerful_questions: List[Dict[str, Any]] = []
    action_items: List[Dict[str, Any]] = []
    emotional_shifts: List[Dict[str, Any]] = []
    values_beliefs: List[Dict[str, Any]] = []
    communication_patterns: Optional[Dict[str, Any]] = None


class SessionInsightListResponse(BaseModel):
    insights: List[SessionInsightResponse]
    total_count: int
    relationship_id: str
    client_name: str
    coach_name: str


class SessionInsightUpdateRequest(BaseModel):
    session_date: Optional[str] = None
    session_title: Optional[str] = None
    visible_to_client: Optional[bool] = None
    visible_to_coach: Optional[bool] = None