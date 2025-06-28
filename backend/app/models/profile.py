from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
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
    specialties: List[str]
    experience: int
    philosophy: str


class ClientData(BaseModel):
    background: str
    challenges: List[str]


class Profile(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    user_id: str  # Foreign key to User
    clerk_user_id: str  # Clerk user ID for direct integration
    first_name: str
    last_name: str
    coach_data: Optional[CoachData] = None
    client_data: Optional[ClientData] = None
    primary_organization_id: Optional[str] = None  # Clerk organization ID
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)