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


class Quote(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    quote_text: str
    author: str
    source: Optional[str] = None
    category: str  # "motivation" | "leadership" | "growth" | "courage"
    tags: List[str] = Field(default_factory=list)
    display_count: int = 0  # Default 0
    like_count: int = 0  # Default 0
    active: bool = True  # Default true
    created_by: str  # Admin user
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class UserQuoteLike(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    user_id: str
    quote_id: str
    liked_at: datetime = Field(default_factory=datetime.utcnow)