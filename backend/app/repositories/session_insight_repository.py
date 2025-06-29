from typing import List, Optional, Dict, Any
from app.models.session_insight import SessionInsight
from app.db.mongodb import get_database
from bson import ObjectId
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SessionInsightRepository:
    def __init__(self):
        self.collection_name = "session_insights"

    async def create_insight(self, insight: SessionInsight) -> SessionInsight:
        """Create a new session insight"""
        try:
            db = get_database()
            insight_dict = insight.model_dump(by_alias=True, exclude={"id"})
            
            # Remove the id field if it's None or empty
            if "_id" in insight_dict and insight_dict["_id"] is None:
                del insight_dict["_id"]
            
            result = await db[self.collection_name].insert_one(insight_dict)
            
            # Fetch the created insight
            created_insight = await db[self.collection_name].find_one({"_id": result.inserted_id})
            
            # Convert ObjectId to string for Pydantic model
            if created_insight and "_id" in created_insight:
                created_insight["_id"] = str(created_insight["_id"])
            
            return SessionInsight(**created_insight)
            
        except Exception as e:
            logger.error(f"Error creating session insight: {e}")
            raise

    async def get_insight_by_id(self, insight_id: str) -> Optional[SessionInsight]:
        """Get session insight by ID"""
        try:
            if not ObjectId.is_valid(insight_id):
                return None
                
            db = get_database()
            insight_data = await db[self.collection_name].find_one({"_id": ObjectId(insight_id)})
            
            if insight_data:
                # Convert ObjectId to string for Pydantic model
                insight_data["_id"] = str(insight_data["_id"])
                return SessionInsight(**insight_data)
            return None
            
        except Exception as e:
            logger.error(f"Error fetching insight {insight_id}: {e}")
            return None

    async def get_insights_by_relationship(
        self, 
        relationship_id: str,
        limit: int = 20,
        offset: int = 0
    ) -> List[SessionInsight]:
        """Get session insights for a coaching relationship"""
        try:
            db = get_database()
            cursor = db[self.collection_name].find(
                {"coaching_relationship_id": relationship_id}
            ).sort("session_date", -1).skip(offset).limit(limit)
            
            insights = []
            async for insight_data in cursor:
                # Convert ObjectId to string for Pydantic model
                if "_id" in insight_data:
                    insight_data["_id"] = str(insight_data["_id"])
                insights.append(SessionInsight(**insight_data))
            
            return insights
            
        except Exception as e:
            logger.error(f"Error fetching insights for relationship {relationship_id}: {e}")
            return []

    async def update_insight(self, insight_id: str, update_data: Dict[str, Any]) -> Optional[SessionInsight]:
        """Update session insight"""
        try:
            if not ObjectId.is_valid(insight_id):
                return None
            
            db = get_database()
            update_data["updated_at"] = datetime.utcnow()
            
            result = await db[self.collection_name].update_one(
                {"_id": ObjectId(insight_id)},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                return await self.get_insight_by_id(insight_id)
            return None
            
        except Exception as e:
            logger.error(f"Error updating insight {insight_id}: {e}")
            return None

    async def delete_insight(self, insight_id: str) -> bool:
        """Delete session insight"""
        try:
            if not ObjectId.is_valid(insight_id):
                return False
                
            db = get_database()
            result = await db[self.collection_name].delete_one({"_id": ObjectId(insight_id)})
            return result.deleted_count > 0
            
        except Exception as e:
            logger.error(f"Error deleting insight {insight_id}: {e}")
            return False

    async def get_insights_count_by_relationship(self, relationship_id: str) -> int:
        """Get total count of insights for a relationship"""
        try:
            db = get_database()
            return await db[self.collection_name].count_documents(
                {"coaching_relationship_id": relationship_id}
            )
        except Exception as e:
            logger.error(f"Error counting insights for relationship {relationship_id}: {e}")
            return 0

    async def get_insights_by_user(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0
    ) -> List[SessionInsight]:
        """Get session insights where user is either coach or client"""
        try:
            db = get_database()
            cursor = db[self.collection_name].find({
                "$or": [
                    {"coach_user_id": user_id},
                    {"client_user_id": user_id}
                ]
            }).sort("created_at", -1).skip(offset).limit(limit)
            
            insights = []
            async for insight_data in cursor:
                # Convert ObjectId to string for Pydantic model
                if "_id" in insight_data:
                    insight_data["_id"] = str(insight_data["_id"])
                insights.append(SessionInsight(**insight_data))
            
            return insights
            
        except Exception as e:
            logger.error(f"Error fetching insights for user {user_id}: {e}")
            return []