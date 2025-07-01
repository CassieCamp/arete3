from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from app.models.notification import Notification, NotificationType, NotificationPriority, NotificationAction
from app.repositories.notification_repository import NotificationRepository
from app.services.user_service import UserService
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self):
        self.notification_repository = NotificationRepository()
        self.user_service = UserService()
    
    async def create_notification(
        self,
        user_id: str,
        title: str,
        message: str,
        notification_type: NotificationType,
        priority: NotificationPriority = NotificationPriority.MEDIUM,
        related_entity_id: Optional[str] = None,
        related_entity_type: Optional[str] = None,
        actions: List[NotificationAction] = None,
        metadata: Dict[str, Any] = None,
        expires_in_days: Optional[int] = 30
    ) -> Notification:
        """Create a new notification"""
        try:
            logger.info(f"=== NotificationService.create_notification called ===")
            logger.info(f"user_id: {user_id}, type: {notification_type}")
            
            expires_at = None
            if expires_in_days:
                expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
            
            notification = Notification(
                user_id=user_id,
                title=title,
                message=message,
                type=notification_type,
                priority=priority,
                related_entity_id=related_entity_id,
                related_entity_type=related_entity_type,
                actions=actions or [],
                metadata=metadata or {},
                expires_at=expires_at
            )
            
            saved_notification = await self.notification_repository.create_notification(notification)
            logger.info(f"✅ Created notification: {saved_notification.id}")
            
            # Trigger real-time delivery (WebSocket, etc.)
            await self._deliver_notification(saved_notification)
            
            return saved_notification
            
        except Exception as e:
            logger.error(f"❌ Error creating notification: {e}")
            raise
    
    async def get_user_notifications(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0,
        unread_only: bool = False
    ) -> List[Notification]:
        """Get notifications for a user"""
        try:
            return await self.notification_repository.get_user_notifications(
                user_id, limit, offset, unread_only
            )
        except Exception as e:
            logger.error(f"Error fetching notifications for user {user_id}: {e}")
            return []
    
    async def get_unread_count(self, user_id: str) -> int:
        """Get count of unread notifications for a user"""
        try:
            return await self.notification_repository.get_unread_count(user_id)
        except Exception as e:
            logger.error(f"Error getting unread count for user {user_id}: {e}")
            return 0
    
    async def mark_as_read(self, notification_id: str, user_id: str) -> bool:
        """Mark notification as read"""
        try:
            return await self.notification_repository.mark_as_read(notification_id, user_id)
        except Exception as e:
            logger.error(f"Error marking notification as read: {e}")
            return False
    
    async def mark_all_as_read(self, user_id: str) -> int:
        """Mark all notifications as read for a user"""
        try:
            return await self.notification_repository.mark_all_as_read(user_id)
        except Exception as e:
            logger.error(f"Error marking all notifications as read: {e}")
            return 0
    
    async def dismiss_notification(self, notification_id: str, user_id: str) -> bool:
        """Dismiss a notification"""
        try:
            return await self.notification_repository.dismiss_notification(notification_id, user_id)
        except Exception as e:
            logger.error(f"Error dismissing notification: {e}")
            return False
    
    # Notification creation helpers for common events
    
    async def notify_session_insight_completed(
        self,
        user_id: str,
        insight_id: str,
        session_title: Optional[str] = None
    ):
        """Notify when session insight is completed"""
        title = "Session Insight Ready"
        message = f"Your session insight{f' for {session_title}' if session_title else ''} has been generated and is ready to view."
        
        actions = [
            NotificationAction(
                label="View Insight",
                url=f"/dashboard/insights/{insight_id}",
                action_type="navigate"
            )
        ]
        
        await self.create_notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=NotificationType.SESSION_INSIGHT,
            priority=NotificationPriority.MEDIUM,
            related_entity_id=insight_id,
            related_entity_type="session_insight",
            actions=actions
        )
    
    async def notify_baseline_generated(
        self,
        user_id: str,
        baseline_id: str
    ):
        """Notify when baseline is generated"""
        title = "Baseline Analysis Complete"
        message = "Your AI-powered baseline analysis has been completed and is ready to review."
        
        actions = [
            NotificationAction(
                label="View Baseline",
                url="/dashboard/documents",
                action_type="navigate"
            )
        ]
        
        await self.create_notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=NotificationType.BASELINE_GENERATED,
            priority=NotificationPriority.HIGH,
            related_entity_id=baseline_id,
            related_entity_type="baseline",
            actions=actions
        )
    
    async def notify_coaching_relationship_update(
        self,
        user_id: str,
        relationship_id: str,
        update_type: str,
        other_user_name: str
    ):
        """Notify about coaching relationship updates"""
        title_map = {
            "request_received": "New Coaching Request",
            "request_accepted": "Coaching Request Accepted",
            "request_declined": "Coaching Request Declined"
        }
        
        message_map = {
            "request_received": f"{other_user_name} has sent you a coaching relationship request.",
            "request_accepted": f"{other_user_name} has accepted your coaching relationship request.",
            "request_declined": f"{other_user_name} has declined your coaching relationship request."
        }
        
        title = title_map.get(update_type, "Coaching Relationship Update")
        message = message_map.get(update_type, f"Update from {other_user_name}")
        
        actions = [
            NotificationAction(
                label="View Connections",
                url="/dashboard/connections",
                action_type="navigate"
            )
        ]
        
        await self.create_notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=NotificationType.COACHING_RELATIONSHIP,
            priority=NotificationPriority.HIGH,
            related_entity_id=relationship_id,
            related_entity_type="coaching_relationship",
            actions=actions
        )
    
    async def notify_goal_update(
        self,
        user_id: str,
        goal_id: str,
        goal_title: str,
        update_type: str
    ):
        """Notify about goal updates"""
        title_map = {
            "created": "New Goal Created",
            "completed": "Goal Completed",
            "progress_updated": "Goal Progress Updated"
        }
        
        message_map = {
            "created": f"Your new goal '{goal_title}' has been created successfully.",
            "completed": f"Congratulations! You've completed your goal '{goal_title}'.",
            "progress_updated": f"Progress has been updated for your goal '{goal_title}'."
        }
        
        title = title_map.get(update_type, "Goal Update")
        message = message_map.get(update_type, f"Update for goal '{goal_title}'")
        
        actions = [
            NotificationAction(
                label="View Goals",
                url="/dashboard/goals",
                action_type="navigate"
            )
        ]
        
        await self.create_notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=NotificationType.GOAL_UPDATE,
            priority=NotificationPriority.MEDIUM,
            related_entity_id=goal_id,
            related_entity_type="goal",
            actions=actions
        )
    
    async def notify_document_processed(
        self,
        user_id: str,
        document_id: str,
        document_name: str
    ):
        """Notify when document processing is complete"""
        title = "Document Processed"
        message = f"Your document '{document_name}' has been processed and is ready for analysis."
        
        actions = [
            NotificationAction(
                label="View Documents",
                url="/dashboard/documents",
                action_type="navigate"
            )
        ]
        
        await self.create_notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=NotificationType.DOCUMENT_PROCESSED,
            priority=NotificationPriority.MEDIUM,
            related_entity_id=document_id,
            related_entity_type="document",
            actions=actions
        )
    
    async def notify_system_update(
        self,
        user_id: str,
        title: str,
        message: str,
        priority: NotificationPriority = NotificationPriority.LOW
    ):
        """Send a system update notification"""
        await self.create_notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=NotificationType.SYSTEM_UPDATE,
            priority=priority
        )
    
    async def _deliver_notification(self, notification: Notification):
        """Handle notification delivery (WebSocket, email, etc.)"""
        try:
            # Import here to avoid circular imports
            from app.services.websocket_service import websocket_service
            
            # Send via WebSocket if user is connected
            await websocket_service.send_notification_to_user(
                notification.user_id,
                notification
            )
            
            logger.info(f"Delivered notification {notification.id} to user {notification.user_id}")
        except Exception as e:
            logger.error(f"Error delivering notification {notification.id}: {e}")
            # Don't raise the error as notification creation should still succeed
    
    async def cleanup_expired_notifications(self) -> int:
        """Clean up expired notifications"""
        try:
            return await self.notification_repository.cleanup_expired_notifications()
        except Exception as e:
            logger.error(f"Error cleaning up expired notifications: {e}")
            return 0