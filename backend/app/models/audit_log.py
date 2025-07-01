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


class AuditOperation(str, Enum):
    CREATE_RELATIONSHIP = "CREATE_RELATIONSHIP"
    UPDATE_RELATIONSHIP = "UPDATE_RELATIONSHIP"
    DELETE_RELATIONSHIP = "DELETE_RELATIONSHIP"
    SOFT_DELETE_RELATIONSHIP = "SOFT_DELETE_RELATIONSHIP"
    RESTORE_RELATIONSHIP = "RESTORE_RELATIONSHIP"
    MASS_DELETE_DETECTED = "MASS_DELETE_DETECTED"
    INTEGRITY_CHECK_FAILED = "INTEGRITY_CHECK_FAILED"
    BACKUP_CREATED = "BACKUP_CREATED"
    BACKUP_RESTORED = "BACKUP_RESTORED"


class AuditSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class AuditLog(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    
    # Core audit information
    operation: AuditOperation
    severity: AuditSeverity
    entity_type: str  # "coaching_relationship", "session_insight", etc.
    entity_id: Optional[str] = None  # ID of the affected entity
    
    # Context information
    user_id: Optional[str] = None  # User who performed the action
    session_id: Optional[str] = None  # Session identifier if available
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    # Operation details
    operation_details: Dict[str, Any] = Field(default_factory=dict)
    before_state: Optional[Dict[str, Any]] = None  # State before change
    after_state: Optional[Dict[str, Any]] = None   # State after change
    
    # Technical details
    stack_trace: Optional[str] = None
    error_message: Optional[str] = None
    environment: str = "development"  # "development", "staging", "production"
    
    # Metadata
    message: str  # Human-readable description
    tags: list[str] = Field(default_factory=list)  # For categorization
    
    # Timestamps
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Retention
    expires_at: Optional[datetime] = None  # For automatic cleanup