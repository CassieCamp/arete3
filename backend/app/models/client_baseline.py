from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List, Dict, Any
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

class BaselineStatus(str, Enum):
    """Status of baseline generation"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class PersonalityInsight(BaseModel):
    """Individual personality trait or characteristic"""
    trait: str  # e.g., "Communication Style", "Decision Making"
    description: str  # Detailed description of the trait
    evidence: List[str]  # Quotes or examples from documents
    confidence_score: float = Field(ge=0.0, le=1.0)  # AI confidence in this insight

class GoalPattern(BaseModel):
    """Identified goal-setting patterns and preferences"""
    pattern_type: str  # e.g., "Achievement-Oriented", "Relationship-Focused"
    description: str
    examples: List[str]  # Specific examples from documents
    suggested_approach: str  # Coaching approach recommendation

class CommunicationStyle(BaseModel):
    """Communication preferences and patterns"""
    primary_style: str  # e.g., "Direct", "Collaborative", "Analytical"
    characteristics: List[str]  # Specific communication traits
    preferences: List[str]  # Preferred communication methods/styles
    examples: List[str]  # Evidence from documents

class InitialChallenge(BaseModel):
    """Identified challenges or areas for development"""
    challenge_area: str  # e.g., "Time Management", "Team Leadership"
    description: str
    impact_level: str  # "Low", "Medium", "High"
    suggested_focus: str  # Coaching recommendation
    supporting_evidence: List[str]

class BaselineMetadata(BaseModel):
    """Metadata about the baseline generation process"""
    ai_provider: str  # "openai" or "anthropic"
    model_version: str  # e.g., "gpt-4", "claude-3"
    processing_time_seconds: float
    document_count: int
    total_text_length: int
    generation_prompt_version: str  # For tracking prompt iterations

class ClientBaseline(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    user_id: str  # Foreign key to User (client)
    clerk_user_id: str  # Clerk user ID for direct integration
    
    # Core baseline content
    executive_summary: str  # High-level overview of the client
    personality_insights: List[PersonalityInsight] = Field(default_factory=list)
    communication_style: Optional[CommunicationStyle] = None
    goal_patterns: List[GoalPattern] = Field(default_factory=list)
    initial_challenges: List[InitialChallenge] = Field(default_factory=list)
    strengths: List[str] = Field(default_factory=list)  # Identified strengths
    development_opportunities: List[str] = Field(default_factory=list)
    
    # Source information
    source_document_ids: List[str] = Field(default_factory=list)  # Documents analyzed
    analysis_scope: str  # Description of what was analyzed
    
    # Processing metadata
    status: BaselineStatus = BaselineStatus.PENDING
    processing_error: Optional[str] = None
    metadata: Optional[BaselineMetadata] = None
    
    # Access control
    generated_by: str  # User ID of who triggered generation
    visible_to_client: bool = True  # Always true based on requirements
    visible_to_coach: bool = True   # Always true based on requirements
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    def __str__(self) -> str:
        return f"ClientBaseline(user_id='{self.user_id}', status='{self.status}', created_at='{self.created_at}')"