from fastapi import APIRouter, Depends, HTTPException, status, Query, WebSocket, WebSocketDisconnect
from typing import List, Optional
from app.schemas.notification import (
    NotificationResponse, NotificationListResponse, NotificationUpdateRequest,
    MarkAsReadRequest, NotificationActionResponse
)
from app.services.notification_service import NotificationService
from app.services.websocket_service import websocket_service
from app.api.v1.deps import get_current_user, get_current_user_websocket
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=NotificationListResponse)
async def get_notifications(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    unread_only: bool = Query(False),
    current_user: dict = Depends(get_current_user)
):
    """Get notifications for the current user"""
    logger.info(f"=== GET /notifications called ===")
    logger.info(f"Getting notifications for user: {current_user.get('user_id')}")
    logger.info(f"Params - limit: {limit}, offset: {offset}, unread_only: {unread_only}")
    
    try:
        notification_service = NotificationService()
        user_id = current_user["user_id"]
        
        # Get notifications
        notifications = await notification_service.get_user_notifications(
            user_id, limit, offset, unread_only
        )
        
        # Get unread count
        unread_count = await notification_service.get_unread_count(user_id)
        
        # Convert to response format
        notification_responses = []
        for notification in notifications:
            action_responses = [
                NotificationActionResponse(
                    label=action.label,
                    url=action.url,
                    action_type=action.action_type
                ) for action in notification.actions
            ]
            
            notification_responses.append(NotificationResponse(
                id=str(notification.id),
                user_id=notification.user_id,
                title=notification.title,
                message=notification.message,
                type=notification.type,
                priority=notification.priority,
                related_entity_id=notification.related_entity_id,
                related_entity_type=notification.related_entity_type,
                actions=action_responses,
                metadata=notification.metadata,
                is_read=notification.is_read,
                is_dismissed=notification.is_dismissed,
                read_at=notification.read_at,
                dismissed_at=notification.dismissed_at,
                delivery_method=notification.delivery_method,
                delivered_at=notification.delivered_at,
                created_at=notification.created_at,
                expires_at=notification.expires_at
            ))
        
        # Check if there are more notifications
        has_more = len(notifications) == limit
        
        response = NotificationListResponse(
            notifications=notification_responses,
            total_count=len(notification_responses),
            unread_count=unread_count,
            has_more=has_more
        )
        
        logger.info(f"✅ Successfully retrieved {len(notification_responses)} notifications")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error getting notifications: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get notifications: {str(e)}"
        )


@router.get("/unread-count")
async def get_unread_count(
    current_user: dict = Depends(get_current_user)
):
    """Get count of unread notifications for the current user"""
    logger.info(f"=== GET /notifications/unread-count called ===")
    logger.info(f"Getting unread count for user: {current_user.get('user_id')}")
    
    try:
        notification_service = NotificationService()
        user_id = current_user["user_id"]
        
        unread_count = await notification_service.get_unread_count(user_id)
        
        logger.info(f"✅ Successfully retrieved unread count: {unread_count}")
        return {"unread_count": unread_count}
        
    except Exception as e:
        logger.error(f"❌ Error getting unread count: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get unread count: {str(e)}"
        )


@router.post("/{notification_id}/read", status_code=status.HTTP_200_OK)
async def mark_notification_as_read(
    notification_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Mark a specific notification as read"""
    logger.info(f"=== POST /notifications/{notification_id}/read called ===")
    logger.info(f"Marking notification as read for user: {current_user.get('user_id')}")
    
    try:
        notification_service = NotificationService()
        user_id = current_user["user_id"]
        
        success = await notification_service.mark_as_read(notification_id, user_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found or already read"
            )
        
        logger.info(f"✅ Successfully marked notification {notification_id} as read")
        return {"message": "Notification marked as read", "success": True}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error marking notification as read: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark notification as read: {str(e)}"
        )


@router.post("/mark-all-read", status_code=status.HTTP_200_OK)
async def mark_all_notifications_as_read(
    current_user: dict = Depends(get_current_user)
):
    """Mark all notifications as read for the current user"""
    logger.info(f"=== POST /notifications/mark-all-read called ===")
    logger.info(f"Marking all notifications as read for user: {current_user.get('user_id')}")
    
    try:
        notification_service = NotificationService()
        user_id = current_user["user_id"]
        
        count = await notification_service.mark_all_as_read(user_id)
        
        logger.info(f"✅ Successfully marked {count} notifications as read")
        return {"message": f"Marked {count} notifications as read", "count": count}
        
    except Exception as e:
        logger.error(f"❌ Error marking all notifications as read: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark all notifications as read: {str(e)}"
        )


@router.post("/{notification_id}/dismiss", status_code=status.HTTP_200_OK)
async def dismiss_notification(
    notification_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Dismiss a specific notification"""
    logger.info(f"=== POST /notifications/{notification_id}/dismiss called ===")
    logger.info(f"Dismissing notification for user: {current_user.get('user_id')}")
    
    try:
        notification_service = NotificationService()
        user_id = current_user["user_id"]
        
        success = await notification_service.dismiss_notification(notification_id, user_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found or already dismissed"
            )
        
        logger.info(f"✅ Successfully dismissed notification {notification_id}")
        return {"message": "Notification dismissed", "success": True}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error dismissing notification: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to dismiss notification: {str(e)}"
        )


@router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification(
    notification_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific notification by ID"""
    logger.info(f"=== GET /notifications/{notification_id} called ===")
    logger.info(f"Getting notification for user: {current_user.get('user_id')}")
    
    try:
        notification_service = NotificationService()
        user_id = current_user["user_id"]
        
        # Get all user notifications and find the specific one
        # This ensures the user has permission to view this notification
        notifications = await notification_service.get_user_notifications(user_id, limit=1000)
        
        notification = None
        for notif in notifications:
            if str(notif.id) == notification_id:
                notification = notif
                break
        
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        # Convert to response format
        action_responses = [
            NotificationActionResponse(
                label=action.label,
                url=action.url,
                action_type=action.action_type
            ) for action in notification.actions
        ]
        
        response = NotificationResponse(
            id=str(notification.id),
            user_id=notification.user_id,
            title=notification.title,
            message=notification.message,
            type=notification.type,
            priority=notification.priority,
            related_entity_id=notification.related_entity_id,
            related_entity_type=notification.related_entity_type,
            actions=action_responses,
            metadata=notification.metadata,
            is_read=notification.is_read,
            is_dismissed=notification.is_dismissed,
            read_at=notification.read_at,
            dismissed_at=notification.dismissed_at,
            delivery_method=notification.delivery_method,
            delivered_at=notification.delivered_at,
            created_at=notification.created_at,
            expires_at=notification.expires_at
        )
        
        logger.info(f"✅ Successfully retrieved notification {notification_id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting notification: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get notification: {str(e)}"
        )


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    """WebSocket endpoint for real-time notifications"""
    logger.info("=== WebSocket connection attempt ===")
    
    try:
        # Accept the WebSocket connection first
        logger.info("🔗 Accepting WebSocket connection in endpoint...")
        await websocket.accept()
        logger.info("✅ WebSocket connection accepted in endpoint")
        
        # Get user from WebSocket token
        user = await get_current_user_websocket(websocket, token)
        user_id = user["user_id"]
        
        logger.info(f"WebSocket connecting for user: {user_id}")
        
        # Connect the WebSocket (should NOT accept again)
        logger.info("🔗 Calling websocket_service.connect()...")
        await websocket_service.connect(websocket, user_id)
        logger.info("✅ websocket_service.connect() completed")
        
        try:
            # Keep the connection alive and handle incoming messages
            while True:
                # Wait for messages from client (like ping/pong)
                data = await websocket.receive_text()
                logger.info(f"Received WebSocket message from {user_id}: {data}")
                
                # Echo back or handle specific message types
                if data == "ping":
                    await websocket.send_text("pong")
                    
        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected for user {user_id}")
        except Exception as e:
            logger.error(f"WebSocket error for user {user_id}: {e}")
        finally:
            websocket_service.disconnect(websocket, user_id)
            
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
        try:
            await websocket.close(code=1008, reason="Authentication failed")
        except:
            pass


@router.post("/test")
async def create_test_notification(
    current_user: dict = Depends(get_current_user)
):
    """Create a test notification for development purposes"""
    logger.info("=== Creating test notification ===")
    
    try:
        notification_service = NotificationService()
        user_id = current_user["user_id"]
        
        # Create a test notification
        await notification_service.notify_system_update(
            user_id=user_id,
            title="Test Notification",
            message="This is a test notification to verify the real-time notification system is working correctly."
        )
        
        logger.info(f"✅ Created test notification for user {user_id}")
        return {"message": "Test notification created successfully"}
        
    except Exception as e:
        logger.error(f"❌ Error creating test notification: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create test notification: {str(e)}"
        )