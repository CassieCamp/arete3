from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List, Dict, Any
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


class User(BaseModel):
    """User model aligned with standardized Clerk role architecture"""
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    clerk_user_id: str
    email: str
    
    # Standardized role system from Clerk publicMetadata
    primary_role: str = Field(default="member", description="Primary role: admin, coach, or member")
    organization_roles: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Organization-specific roles and permissions from Clerk publicMetadata"
    )
    # Format: {"org_123": {"role": "admin", "permissions": ["manage_members", "view_analytics"]}}
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)