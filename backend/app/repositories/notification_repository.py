from typing import Optional, List
from bson import ObjectId
from datetime import datetime
from app.models.notification import Notification
from app.db.mongodb import get_database
import logging

logger = logging.getLogger(__name__)


class NotificationRepository:
    def __init__(self):
        self.collection_name = "notifications"

    async def create_notification(self, notification: Notification) -> Notification:
        """Create a new notification"""
        logger.info(f"=== NotificationRepository.create_notification called ===")
        logger.info(f"Creating notification for user: {notification.user_id}")
        
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                raise Exception("Database connection is None")
            
            notification_dict = notification.dict(by_alias=True, exclude_unset=True)
            
            # Remove the id field if it's None or empty
            if "_id" in notification_dict and notification_dict["_id"] is None:
                del notification_dict["_id"]
            
            logger.info(f"Inserting notification: {notification_dict}")
            result = await db[self.collection_name].insert_one(notification_dict)
            
            notification.id = result.inserted_id
            logger.info(f"✅ Successfully created notification with ID: {notification.id}")
            return notification
            
        except Exception as e:
            logger.error(f"❌ Error creating notification: {e}")
            raise

    async def get_notification_by_id(self, notification_id: str) -> Optional[Notification]:
        """Get notification by ID"""
        logger.info(f"=== NotificationRepository.get_notification_by_id called ===")
        logger.info(f"Getting notification: {notification_id}")
        
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                raise Exception("Database connection is None")
            
            notification_doc = await db[self.collection_name].find_one({"_id": ObjectId(notification_id)})
            
            if notification_doc:
                # Convert ObjectId to string for Pydantic compatibility
                if "_id" in notification_doc and notification_doc["_id"]:
                    notification_doc["_id"] = str(notification_doc["_id"])
                
                notification = Notification(**notification_doc)
                logger.info(f"✅ Found notification: {notification.id}")
                return notification
            
            logger.info("Notification not found")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting notification: {e}")
            raise

    async def get_user_notifications(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0,
        unread_only: bool = False
    ) -> List[Notification]:
        """Get notifications for a user"""
        logger.info(f"=== NotificationRepository.get_user_notifications called ===")
        logger.info(f"Getting notifications for user: {user_id}, limit: {limit}, offset: {offset}, unread_only: {unread_only}")
        
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                raise Exception("Database connection is None")
            
            # Build query
            query = {"user_id": user_id}
            if unread_only:
                query["is_read"] = False
            
            # Add expiration filter - exclude expired notifications
            query["$or"] = [
                {"expires_at": {"$exists": False}},
                {"expires_at": None},
                {"expires_at": {"$gt": datetime.utcnow()}}
            ]
            
            logger.info(f"Query: {query}")
            
            # Execute query with sorting, limit, and offset
            cursor = db[self.collection_name].find(query).sort("created_at", -1).skip(offset).limit(limit)
            notification_docs = await cursor.to_list(length=limit)
            
            notifications = []
            for doc in notification_docs:
                # Convert ObjectId to string for Pydantic compatibility
                if "_id" in doc and doc["_id"]:
                    doc["_id"] = str(doc["_id"])
                notifications.append(Notification(**doc))
            
            logger.info(f"✅ Found {len(notifications)} notifications for user {user_id}")
            return notifications
            
        except Exception as e:
            logger.error(f"❌ Error getting user notifications: {e}")
            raise

    async def get_unread_count(self, user_id: str) -> int:
        """Get count of unread notifications for a user"""
        logger.info(f"=== NotificationRepository.get_unread_count called ===")
        logger.info(f"Getting unread count for user: {user_id}")
        
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                raise Exception("Database connection is None")
            
            query = {
                "user_id": user_id,
                "is_read": False,
                "$or": [
                    {"expires_at": {"$exists": False}},
                    {"expires_at": None},
                    {"expires_at": {"$gt": datetime.utcnow()}}
                ]
            }
            
            count = await db[self.collection_name].count_documents(query)
            logger.info(f"✅ Found {count} unread notifications for user {user_id}")
            return count
            
        except Exception as e:
            logger.error(f"❌ Error getting unread count: {e}")
            return 0

    async def mark_as_read(self, notification_id: str, user_id: str) -> bool:
        """Mark a notification as read"""
        logger.info(f"=== NotificationRepository.mark_as_read called ===")
        logger.info(f"Marking notification {notification_id} as read for user {user_id}")
        
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                raise Exception("Database connection is None")
            
            result = await db[self.collection_name].update_one(
                {"_id": ObjectId(notification_id), "user_id": user_id},
                {
                    "$set": {
                        "is_read": True,
                        "read_at": datetime.utcnow()
                    }
                }
            )
            
            success = result.modified_count > 0
            if success:
                logger.info(f"✅ Successfully marked notification {notification_id} as read")
            else:
                logger.warning(f"Notification {notification_id} was not marked as read (not found or no permission)")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error marking notification as read: {e}")
            return False

    async def mark_all_as_read(self, user_id: str) -> int:
        """Mark all notifications as read for a user"""
        logger.info(f"=== NotificationRepository.mark_all_as_read called ===")
        logger.info(f"Marking all notifications as read for user: {user_id}")
        
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                raise Exception("Database connection is None")
            
            result = await db[self.collection_name].update_many(
                {"user_id": user_id, "is_read": False},
                {
                    "$set": {
                        "is_read": True,
                        "read_at": datetime.utcnow()
                    }
                }
            )
            
            count = result.modified_count
            logger.info(f"✅ Successfully marked {count} notifications as read for user {user_id}")
            return count
            
        except Exception as e:
            logger.error(f"❌ Error marking all notifications as read: {e}")
            return 0

    async def dismiss_notification(self, notification_id: str, user_id: str) -> bool:
        """Dismiss a notification"""
        logger.info(f"=== NotificationRepository.dismiss_notification called ===")
        logger.info(f"Dismissing notification {notification_id} for user {user_id}")
        
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                raise Exception("Database connection is None")
            
            result = await db[self.collection_name].update_one(
                {"_id": ObjectId(notification_id), "user_id": user_id},
                {
                    "$set": {
                        "is_dismissed": True,
                        "dismissed_at": datetime.utcnow()
                    }
                }
            )
            
            success = result.modified_count > 0
            if success:
                logger.info(f"✅ Successfully dismissed notification {notification_id}")
            else:
                logger.warning(f"Notification {notification_id} was not dismissed (not found or no permission)")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error dismissing notification: {e}")
            return False

    async def delete_notification(self, notification_id: str, user_id: str) -> bool:
        """Delete a notification"""
        logger.info(f"=== NotificationRepository.delete_notification called ===")
        logger.info(f"Deleting notification {notification_id} for user {user_id}")
        
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                raise Exception("Database connection is None")
            
            result = await db[self.collection_name].delete_one(
                {"_id": ObjectId(notification_id), "user_id": user_id}
            )
            
            success = result.deleted_count > 0
            if success:
                logger.info(f"✅ Successfully deleted notification {notification_id}")
            else:
                logger.warning(f"Notification {notification_id} was not deleted (not found or no permission)")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error deleting notification: {e}")
            return False

    async def cleanup_expired_notifications(self) -> int:
        """Clean up expired notifications"""
        logger.info(f"=== NotificationRepository.cleanup_expired_notifications called ===")
        
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                raise Exception("Database connection is None")
            
            result = await db[self.collection_name].delete_many({
                "expires_at": {"$lt": datetime.utcnow()}
            })
            
            count = result.deleted_count
            logger.info(f"✅ Cleaned up {count} expired notifications")
            return count
            
        except Exception as e:
            logger.error(f"❌ Error cleaning up expired notifications: {e}")
            return 0