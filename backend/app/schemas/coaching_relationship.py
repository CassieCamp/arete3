from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from app.models.coaching_relationship import RelationshipStatus


class ConnectionRequestCreate(BaseModel):
    """Schema for creating a connection request (coach-initiated)"""
    client_email: str = Field(..., description="Email of the client to invite")


class ConnectionRequestResponse(BaseModel):
    """Schema for responding to a connection request"""
    status: RelationshipStatus = Field(..., description="Response status: 'active' to accept, 'declined' to decline")


class CoachingRelationshipResponse(BaseModel):
    """Schema for coaching relationship response"""
    id: str = Field(..., description="Relationship ID")
    coach_user_id: str = Field(..., description="Coach user ID")
    client_user_id: str = Field(..., description="Client user ID")
    coach_email: Optional[str] = Field(None, description="Coach email address")
    client_email: Optional[str] = Field(None, description="Client email address")
    status: RelationshipStatus = Field(..., description="Relationship status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class UserRelationshipsResponse(BaseModel):
    """Schema for user's relationships response"""
    pending: List[CoachingRelationshipResponse] = Field(..., description="Pending connection requests")
    active: List[CoachingRelationshipResponse] = Field(..., description="Active coaching relationships")