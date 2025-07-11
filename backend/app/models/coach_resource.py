from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List
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


class CoachResource(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    coach_user_id: str
    title: str
    description: Optional[str] = None
    resource_url: str
    resource_type: str  # "document" | "article" | "video" | "tool"
    is_template: bool = False  # Default false
    client_specific: bool = False  # Default false
    target_client_id: Optional[str] = None
    category: str  # "exercise" | "assessment" | "reading" | "framework"
    tags: List[str] = Field(default_factory=list)
    active: bool = True  # Default true
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class CoachClientNote(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    coach_user_id: str
    client_user_id: str
    note_of_moment: Optional[str] = None
    way_of_working: Optional[str] = None
    about_me: Optional[str] = None
    way_of_working_template_id: Optional[str] = None
    about_me_template_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)