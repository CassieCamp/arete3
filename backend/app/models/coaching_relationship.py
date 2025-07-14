from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, Dict, Any
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


class RelationshipStatus(str, Enum):
    PENDING = "pending"  # NEW: Simplified pending status
    ACTIVE = "active"
    INACTIVE = "inactive"  # NEW: For inactive relationships
    DECLINED = "declined"
    DELETED = "deleted"  # For soft delete
    # Legacy statuses for backward compatibility
    PENDING_BY_COACH = "pending_by_coach"


class CoachingRelationship(BaseModel):
    """Enhanced CoachingRelationship model with many-to-many support and organization context"""
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    
    # Many-to-many relationship support
    coach_id: str = Field(..., description="User ID of coach")
    member_id: str = Field(..., description="User ID of member (formerly client)")
    
    # Legacy fields for backward compatibility
    coach_user_id: Optional[str] = Field(default=None, description="Legacy coach user ID field")
    client_user_id: Optional[str] = Field(default=None, description="Legacy client user ID field")
    
    # Organization context
    coach_organization_id: Optional[str] = Field(default=None, description="Coach's organization ID")
    member_organization_id: Optional[str] = Field(default=None, description="Member's organization ID")
    
    # Relationship metadata
    status: RelationshipStatus = RelationshipStatus.PENDING
    start_date: datetime = Field(default_factory=datetime.utcnow, description="Relationship start date")
    end_date: Optional[datetime] = Field(default=None, description="Relationship end date")
    
    # Permissions and access
    permissions: Dict[str, Any] = Field(
        default_factory=dict,
        description="Relationship-specific permissions and access controls"
    )
    
    # Invitation and acceptance tracking
    invited_by_email: Optional[str] = None
    invitation_accepted_at: Optional[datetime] = None
    
    # Freemium transition tracking
    upgraded_from_freemium: bool = False
    upgrade_date: Optional[datetime] = None
    
    # Soft delete fields
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[str] = None
    deletion_reason: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)