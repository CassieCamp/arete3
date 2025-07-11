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


class EntryType(str, Enum):
    SESSION = "session"
    FRESH_THOUGHT = "fresh_thought"


class EntryStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing" 
    COMPLETED = "completed"
    FAILED = "failed"


class DetectedGoal(BaseModel):
    """A goal detected from entry content"""
    goal_statement: str
    confidence: float = Field(ge=0.0, le=1.0)
    suggested: bool = True
    accepted: Optional[bool] = None
    destination_id: Optional[str] = None


class Celebration(BaseModel):
    """A win or achievement to celebrate from the entry"""
    description: str
    significance: str  # Why this is meaningful
    evidence: List[str] = Field(default_factory=list)  # Supporting quotes from content


class Intention(BaseModel):
    """An intention for behavior change discussed during entry"""
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
    """Changes in client's emotional state during entry"""
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


class EntryMetadata(BaseModel):
    """Metadata about the entry and analysis"""
    content_word_count: int
    ai_provider: str
    model_version: str
    processing_time_seconds: float
    analysis_confidence: float = Field(ge=0.0, le=1.0)


class Entry(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    
    # NEW: Unified entry fields
    entry_type: EntryType = EntryType.SESSION
    title: Optional[str] = None  # AI-generated title
    
    # Relationships - Made optional for unpaired entries
    coaching_relationship_id: Optional[str] = None  # Links to CoachingRelationship
    client_user_id: str  # Client (always required)
    coach_user_id: Optional[str] = None   # Coach (optional for unpaired)
    
    # Entry Information
    session_date: Optional[datetime] = None  # When the session occurred
    transcript_content: Optional[str] = None  # For session entries
    content: Optional[str] = None  # For fresh thought entries
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Core Insights (ICF-aligned) - maintained from SessionInsight
    celebrations: List[Celebration] = Field(default_factory=list)
    intentions: List[Intention] = Field(default_factory=list)
    client_discoveries: List[ClientDiscovery] = Field(default_factory=list)
    goal_progress: List[GoalProgress] = Field(default_factory=list)
    coaching_presence: Optional[CoachingPresence] = None
    powerful_questions: List[PowerfulQuestion] = Field(default_factory=list)
    action_items: List[ActionItem] = Field(default_factory=list)
    emotional_shifts: List[EmotionalShift] = Field(default_factory=list)
    values_beliefs: List[ValuesBeliefs] = Field(default_factory=list)
    communication_patterns: Optional[CommunicationPattern] = None
    
    # NEW: Goal Detection
    detected_goals: List[DetectedGoal] = Field(default_factory=list)
    
    # Processing Information
    status: EntryStatus = EntryStatus.PENDING
    processing_error: Optional[str] = None
    overall_session_quality: Optional[str] = None  # For session entries
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None