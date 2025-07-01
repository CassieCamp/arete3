from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any
from app.models.notification import NotificationType, NotificationPriority, NotificationAction


class NotificationActionResponse(BaseModel):
    """Response schema for notification actions"""
    label: str
    url: str
    action_type: str

    class Config:
        from_attributes = True


class NotificationResponse(BaseModel):
    """Response schema for notifications"""
    id: str
    user_id: str
    title: str
    message: str
    type: NotificationType
    priority: NotificationPriority
    related_entity_id: Optional[str] = None
    related_entity_type: Optional[str] = None
    actions: List[NotificationActionResponse] = []
    metadata: Dict[str, Any] = {}
    is_read: bool = False
    is_dismissed: bool = False
    read_at: Optional[datetime] = None
    dismissed_at: Optional[datetime] = None
    delivery_method: List[str] = []
    delivered_at: Optional[datetime] = None
    created_at: datetime
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class NotificationCreateRequest(BaseModel):
    """Request schema for creating notifications"""
    user_id: str
    title: str
    message: str
    type: NotificationType
    priority: Optional[NotificationPriority] = NotificationPriority.MEDIUM
    related_entity_id: Optional[str] = None
    related_entity_type: Optional[str] = None
    actions: Optional[List[NotificationAction]] = []
    metadata: Optional[Dict[str, Any]] = {}
    expires_in_days: Optional[int] = 30


class NotificationUpdateRequest(BaseModel):
    """Request schema for updating notifications"""
    is_read: Optional[bool] = None
    is_dismissed: Optional[bool] = None


class NotificationListResponse(BaseModel):
    """Response schema for notification lists"""
    notifications: List[NotificationResponse]
    total_count: int
    unread_count: int
    has_more: bool


class MarkAsReadRequest(BaseModel):
    """Request schema for marking notifications as read"""
    notification_ids: Optional[List[str]] = None  # If None, mark all as read