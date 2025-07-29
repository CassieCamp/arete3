from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from bson import ObjectId
from datetime import datetime


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


class CoachData(BaseModel):
    specialties: List[str] = Field(default_factory=list)
    experience: Optional[int] = None
    philosophy: Optional[str] = None


class ClientData(BaseModel):
    background: Optional[str] = None
    challenges: List[str] = Field(default_factory=list)


class IdentityFoundation(BaseModel):
    """NEW: Basecamp - Identity Foundation"""
    values: Optional[str] = None
    energy_amplifiers: Optional[str] = None
    energy_drainers: Optional[str] = None
    personality_notes: Optional[str] = None
    clifton_strengths: List[str] = Field(default_factory=list)
    enneagram_type: Optional[str] = None
    disc_profile: Optional[Dict[str, Any]] = None
    myers_briggs: Optional[str] = None


class FreemiumStatus(BaseModel):
    """NEW: Freemium tracking"""
    has_coach: bool = False  # Derive from existing coaching relationships
    entries_count: int = 0  # Count from entries collection
    max_free_entries: int = 3  # Default 3
    coach_requested: bool = False  # Default false
    coach_request_date: Optional[datetime] = None


class DashboardPreferences(BaseModel):
    """NEW: Redesign preferences"""
    preferred_landing_tab: str = "journey"  # Default "journey"
    quote_likes: List[str] = Field(default_factory=list)  # ObjectIds of liked quotes
    onboarding_completed: bool = False  # Default false
    tooltips_shown: bool = False  # Default false


class RedesignFeatures(BaseModel):
    """NEW: Feature flags"""
    unified_entries: bool = False  # Default false
    destinations_rebrand: bool = False  # Default false
    mountain_navigation: bool = False  # Default false
    freemium_gating: bool = False  # Default false


class Profile(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    clerk_user_id: str  # Clerk user ID for direct integration
    first_name: str
    last_name: str
    coach_data: Optional[CoachData] = None
    client_data: Optional[ClientData] = None
    primary_organization_id: Optional[str] = None  # Clerk organization ID
    
    # NEW: Basecamp - Identity Foundation
    identity_foundation: Optional[IdentityFoundation] = None
    
    # NEW: Freemium tracking
    freemium_status: Optional[FreemiumStatus] = None
    
    # NEW: Redesign preferences
    dashboard_preferences: Optional[DashboardPreferences] = None
    
    # NEW: Feature flags
    redesign_features: Optional[RedesignFeatures] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)