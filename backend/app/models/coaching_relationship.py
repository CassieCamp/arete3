from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional
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
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    coach_user_id: str  # ID of the coach user
    client_user_id: str  # ID of the client user
    status: RelationshipStatus = RelationshipStatus.PENDING
    
    # NEW: Pending relationship support
    invited_by_email: Optional[str] = None
    invitation_accepted_at: Optional[datetime] = None
    
    # NEW: Freemium transition tracking
    upgraded_from_freemium: bool = False  # Default false
    upgrade_date: Optional[datetime] = None
    
    # Soft delete fields
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[str] = None  # User ID who deleted the relationship
    deletion_reason: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)