from typing import Dict, Set
from fastapi import WebSocket
from app.models.notification import Notification
import json
import logging

logger = logging.getLogger(__name__)


class WebSocketService:
    def __init__(self):
        # Store active connections by user_id
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        """Store WebSocket connection (connection should already be accepted)"""
        logger.info(f"🔗 WebSocketService.connect() called for user {user_id}")
        logger.info(f"✅ Storing WebSocket connection (already accepted in endpoint)")
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        
        self.active_connections[user_id].add(websocket)
        logger.info(f"✅ WebSocket connected for user {user_id}. Total connections: {len(self.active_connections[user_id])}")

    def disconnect(self, websocket: WebSocket, user_id: str):
        """Remove a WebSocket connection"""
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        
        logger.info(f"WebSocket disconnected for user {user_id}")

    async def send_notification_to_user(self, user_id: str, notification: Notification):
        """Send a notification to all active connections for a user"""
        if user_id not in self.active_connections:
            logger.info(f"No active WebSocket connections for user {user_id}")
            return

        # Prepare notification data
        notification_data = {
            "type": "notification",
            "data": {
                "id": str(notification.id),
                "user_id": notification.user_id,
                "title": notification.title,
                "message": notification.message,
                "type": notification.type,
                "priority": notification.priority,
                "related_entity_id": notification.related_entity_id,
                "related_entity_type": notification.related_entity_type,
                "actions": [
                    {
                        "label": action.label,
                        "url": action.url,
                        "action_type": action.action_type
                    } for action in notification.actions
                ],
                "metadata": notification.metadata,
                "is_read": notification.is_read,
                "is_dismissed": notification.is_dismissed,
                "read_at": notification.read_at.isoformat() if notification.read_at else None,
                "dismissed_at": notification.dismissed_at.isoformat() if notification.dismissed_at else None,
                "delivery_method": notification.delivery_method,
                "delivered_at": notification.delivered_at.isoformat() if notification.delivered_at else None,
                "created_at": notification.created_at.isoformat(),
                "expires_at": notification.expires_at.isoformat() if notification.expires_at else None
            }
        }

        # Send to all connections for this user
        connections_to_remove = set()
        for websocket in self.active_connections[user_id].copy():
            try:
                await websocket.send_text(json.dumps(notification_data))
                logger.info(f"Sent notification {notification.id} to user {user_id} via WebSocket")
            except Exception as e:
                logger.error(f"Error sending notification to WebSocket: {e}")
                connections_to_remove.add(websocket)

        # Remove failed connections
        for websocket in connections_to_remove:
            self.disconnect(websocket, user_id)

    async def send_message_to_user(self, user_id: str, message_type: str, data: dict):
        """Send a custom message to all active connections for a user"""
        if user_id not in self.active_connections:
            logger.info(f"No active WebSocket connections for user {user_id}")
            return

        message = {
            "type": message_type,
            "data": data
        }

        # Send to all connections for this user
        connections_to_remove = set()
        for websocket in self.active_connections[user_id].copy():
            try:
                await websocket.send_text(json.dumps(message))
                logger.info(f"Sent {message_type} message to user {user_id} via WebSocket")
            except Exception as e:
                logger.error(f"Error sending message to WebSocket: {e}")
                connections_to_remove.add(websocket)

        # Remove failed connections
        for websocket in connections_to_remove:
            self.disconnect(websocket, user_id)

    def get_user_connection_count(self, user_id: str) -> int:
        """Get the number of active connections for a user"""
        return len(self.active_connections.get(user_id, set()))

    def get_total_connections(self) -> int:
        """Get the total number of active connections"""
        return sum(len(connections) for connections in self.active_connections.values())


# Global instance
websocket_service = WebSocketService()