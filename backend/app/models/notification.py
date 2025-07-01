from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, Dict, Any, List
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


class NotificationType(str, Enum):
    """Types of notifications"""
    COACHING_RELATIONSHIP = "coaching_relationship"
    SESSION_INSIGHT = "session_insight"
    GOAL_UPDATE = "goal_update"
    BASELINE_GENERATED = "baseline_generated"
    DOCUMENT_PROCESSED = "document_processed"
    SYSTEM_UPDATE = "system_update"


class NotificationPriority(str, Enum):
    """Notification priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class NotificationAction(BaseModel):
    """Action that can be taken from a notification"""
    label: str
    url: str
    action_type: str  # "navigate", "api_call", "modal"


class Notification(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    
    # Target user
    user_id: str  # Who should receive this notification
    
    # Notification content
    title: str
    message: str
    type: NotificationType
    priority: NotificationPriority = NotificationPriority.MEDIUM
    
    # Related entities
    related_entity_id: Optional[str] = None  # ID of related object (session, goal, etc.)
    related_entity_type: Optional[str] = None  # Type of related object
    
    # Actions
    actions: List[NotificationAction] = Field(default_factory=list)
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Status
    is_read: bool = False
    is_dismissed: bool = False
    read_at: Optional[datetime] = None
    dismissed_at: Optional[datetime] = None
    
    # Delivery
    delivery_method: List[str] = Field(default_factory=lambda: ["in_app"])  # in_app, email, push
    delivered_at: Optional[datetime] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None  # Auto-dismiss after this time