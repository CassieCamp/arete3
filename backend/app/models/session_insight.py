from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from bson import ObjectId
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


class SessionInsightStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing" 
    COMPLETED = "completed"
    FAILED = "failed"


class Celebration(BaseModel):
    """A win or achievement to celebrate from the session"""
    description: str
    significance: str  # Why this is meaningful
    evidence: List[str] = Field(default_factory=list)  # Supporting quotes from transcript


class Intention(BaseModel):
    """An intention for behavior change discussed during session"""
    behavior_change: str
    commitment_level: str  # "Strong", "Moderate", "Exploratory"
    timeline: Optional[str] = None
    support_needed: List[str] = Field(default_factory=list)


class ClientDiscovery(BaseModel):
    """New insights the client gained about themselves"""
    insight: str
    depth_level: str  # "Surface", "Moderate", "Deep"
    emotional_response: str  # Client's reaction to the discovery
    evidence: List[str] = Field(default_factory=list)


class GoalProgress(BaseModel):
    """Progress toward stated goals and commitments"""
    goal_area: str
    progress_description: str
    progress_level: str  # "Significant", "Moderate", "Minimal", "Setback"
    barriers_identified: List[str] = Field(default_factory=list)
    next_steps: List[str] = Field(default_factory=list)


class CoachingPresence(BaseModel):
    """Quality of coaching relationship and client engagement"""
    client_engagement_level: str  # "High", "Moderate", "Low"
    rapport_quality: str
    trust_indicators: List[str] = Field(default_factory=list)
    partnership_dynamics: str


class PowerfulQuestion(BaseModel):
    """Questions that led to breakthroughs or deeper reflection"""
    question: str
    impact_description: str
    client_response_summary: str
    breakthrough_level: str  # "Major", "Moderate", "Minor"


class ActionItem(BaseModel):
    """Concrete next steps and commitments identified"""
    action: str
    timeline: Optional[str] = None
    accountability_measure: Optional[str] = None
    client_commitment_level: str  # "High", "Medium", "Low"


class EmotionalShift(BaseModel):
    """Changes in client's emotional state during session"""
    initial_state: str
    final_state: str
    shift_description: str
    catalyst: str  # What caused the shift


class ValuesBeliefs(BaseModel):
    """Core values or limiting beliefs that surfaced"""
    type: str  # "Core Value", "Limiting Belief", "Empowering Belief"
    description: str
    impact_on_goals: str
    exploration_depth: str


class CommunicationPattern(BaseModel):
    """How the client processes information and expresses themselves"""
    processing_style: str  # "Visual", "Auditory", "Kinesthetic", "Mixed"
    expression_patterns: List[str] = Field(default_factory=list)
    communication_preferences: List[str] = Field(default_factory=list)
    notable_changes: List[str] = Field(default_factory=list)


class SessionMetadata(BaseModel):
    """Metadata about the session and analysis"""
    session_duration_minutes: Optional[int] = None
    transcript_word_count: int
    ai_provider: str
    model_version: str
    processing_time_seconds: float
    analysis_confidence: float = Field(ge=0.0, le=1.0)


class SessionInsight(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    
    # Relationships - Made optional for unpaired insights
    coaching_relationship_id: Optional[str] = None  # Links to CoachingRelationship
    client_user_id: str  # Client in the relationship (always required)
    coach_user_id: Optional[str] = None   # Coach in the relationship (optional for unpaired)
    
    # Unpaired insight fields
    is_unpaired: bool = False  # Flag to identify unpaired insights
    shared_with_coaches: List[str] = Field(default_factory=list)  # Coach user IDs with access
    sharing_permissions: Dict[str, Any] = Field(default_factory=dict)  # Granular permissions
    
    # Session Information
    session_date: Optional[datetime] = None  # When the session occurred
    session_title: Optional[str] = None  # Optional session title/topic
    transcript_source: str  # "file_upload", "text_input", "url_import"
    source_document_id: Optional[str] = None  # If uploaded as document
    
    # Core Insights (ICF-aligned)
    celebration: Optional[Celebration] = None
    intention: Optional[Intention] = None
    client_discoveries: List[ClientDiscovery] = Field(default_factory=list)
    goal_progress: List[GoalProgress] = Field(default_factory=list)
    coaching_presence: Optional[CoachingPresence] = None
    powerful_questions: List[PowerfulQuestion] = Field(default_factory=list)
    action_items: List[ActionItem] = Field(default_factory=list)
    emotional_shifts: List[EmotionalShift] = Field(default_factory=list)
    values_beliefs: List[ValuesBeliefs] = Field(default_factory=list)
    communication_patterns: Optional[CommunicationPattern] = None
    
    # Summary & Overview
    session_summary: str  # High-level session overview
    key_themes: List[str] = Field(default_factory=list)
    overall_session_quality: str  # "Excellent", "Good", "Average", "Needs Improvement"
    
    # Processing Information
    status: SessionInsightStatus = SessionInsightStatus.PENDING
    processing_error: Optional[str] = None
    metadata: Optional[SessionMetadata] = None
    
    # Access & Audit
    created_by: str  # User ID who created this insight
    visible_to_client: bool = True
    visible_to_coach: bool = True
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None