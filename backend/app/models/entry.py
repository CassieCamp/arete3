from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from bson import ObjectId

class EntryType(str, Enum):
    REFLECTION = "reflection"
    GOAL = "goal"
    MILESTONE = "milestone"
    INSIGHT = "insight"

class EntryStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class DetectedGoal(BaseModel):
    goal_text: str
    confidence: float
    category: Optional[str] = None

class Entry(BaseModel):
    id: Optional[ObjectId] = Field(default_factory=ObjectId, alias="_id")
    user_id: str
    clerk_user_id: str
    title: str
    content: str
    entry_type: EntryType
    status: EntryStatus = EntryStatus.DRAFT
    detected_goals: List[DetectedGoal] = []
    tags: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}