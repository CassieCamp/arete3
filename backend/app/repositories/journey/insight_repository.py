"""
Journey System Insight Repository

This module contains the repository class for managing insights in MongoDB.
"""

from typing import Optional, List, Dict, Any
from bson import ObjectId
from datetime import datetime
import logging

from app.models.journey.insight import Insight
from app.models.journey.enums import CategoryType, ReviewStatus
from app.db.mongodb import get_database

logger = logging.getLogger(__name__)


class InsightRepository:
    """Repository for managing insights generated from reflection sources"""
    
    def __init__(self):
        self.collection_name = "journey_insights"

    async def create(self, insight: Insight) -> Insight:
        """Create a new insight"""
        logger.info(f"Creating new insight: {insight.title}")
        
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                raise Exception("Database connection is None")
            
            insight_dict = insight.model_dump(by_alias=True, exclude_unset=True)
            
            # Remove the id field if it's None or empty
            if "_id" in insight_dict and insight_dict["_id"] is None:
                del insight_dict["_id"]
            
            result = await db[self.collection_name].insert_one(insight_dict)
            insight.id = result.inserted_id
            
            logger.info(f"✅ Successfully created insight with ID: {insight.id}")
            return insight
            
        except Exception as e:
            logger.error(f"❌ Error creating insight: {e}")
            raise

    async def get_by_id(self, insight_id: str) -> Optional[Insight]:
        """Get insight by ID"""
        logger.info(f"Getting insight by ID: {insight_id}")
        
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                return None
            
            insight_doc = await db[self.collection_name].find_one({"_id": ObjectId(insight_id)})
            
            if insight_doc:
                # Convert ObjectId to string for Pydantic compatibility
                if "_id" in insight_doc and insight_doc["_id"]:
                    insight_doc["_id"] = str(insight_doc["_id"])
                
                insight = Insight(**insight_doc)
                logger.info(f"✅ Found insight: {insight.title}")
                return insight
            
            logger.info("No insight found with that ID")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting insight by ID: {e}")
            raise

    async def get_all_for_user(self, user_id: str, skip: int = 0, limit: int = 100) -> List[Insight]:
        """Get all insights for a user with pagination"""
        logger.info(f"Getting insights for user: {user_id} (skip={skip}, limit={limit})")
        
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                return []
            
            cursor = db[self.collection_name].find({"user_id": user_id}).skip(skip).limit(limit).sort("created_at", -1)
            insight_docs = await cursor.to_list(length=limit)
            
            insights = []
            for doc in insight_docs:
                # Convert ObjectId to string for Pydantic compatibility
                if "_id" in doc and doc["_id"]:
                    doc["_id"] = str(doc["_id"])
                insights.append(Insight(**doc))
            
            logger.info(f"✅ Found {len(insights)} insights for user")
            return insights
            
        except Exception as e:
            logger.error(f"❌ Error getting insights for user: {e}")
            raise

    async def get_by_reflection_id(self, reflection_id: str) -> List[Insight]:
        """Get all insights generated from a specific reflection source"""
        logger.info(f"Getting insights by reflection ID: {reflection_id}")
        
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                return []
            
            cursor = db[self.collection_name].find({"source_id": reflection_id}).sort("created_at", -1)
            insight_docs = await cursor.to_list(length=None)
            
            insights = []
            for doc in insight_docs:
                # Convert ObjectId to string for Pydantic compatibility
                if "_id" in doc and doc["_id"]:
                    doc["_id"] = str(doc["_id"])
                insights.append(Insight(**doc))
            
            logger.info(f"✅ Found {len(insights)} insights for reflection: {reflection_id}")
            return insights
            
        except Exception as e:
            logger.error(f"❌ Error getting insights by reflection ID: {e}")
            raise

    async def get_by_category(self, user_id: str, category: CategoryType, skip: int = 0, limit: int = 100) -> List[Insight]:
        """Get insights by category for a user"""
        logger.info(f"Getting insights by category: {category} for user: {user_id}")
        
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                return []
            
            cursor = db[self.collection_name].find({
                "user_id": user_id,
                "$or": [
                    {"category": category},
                    {"subcategories": category}
                ]
            }).skip(skip).limit(limit).sort("created_at", -1)
            
            insight_docs = await cursor.to_list(length=limit)
            
            insights = []
            for doc in insight_docs:
                # Convert ObjectId to string for Pydantic compatibility
                if "_id" in doc and doc["_id"]:
                    doc["_id"] = str(doc["_id"])
                insights.append(Insight(**doc))
            
            logger.info(f"✅ Found {len(insights)} insights for category: {category}")
            return insights
            
        except Exception as e:
            logger.error(f"❌ Error getting insights by category: {e}")
            raise

    async def get_by_review_status(self, user_id: str, status: ReviewStatus, skip: int = 0, limit: int = 100) -> List[Insight]:
        """Get insights by review status for a user"""
        logger.info(f"Getting insights by review status: {status} for user: {user_id}")
        
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                return []
            
            cursor = db[self.collection_name].find({
                "user_id": user_id,
                "review_status": status
            }).skip(skip).limit(limit).sort("created_at", -1)
            
            insight_docs = await cursor.to_list(length=limit)
            
            insights = []
            for doc in insight_docs:
                # Convert ObjectId to string for Pydantic compatibility
                if "_id" in doc and doc["_id"]:
                    doc["_id"] = str(doc["_id"])
                insights.append(Insight(**doc))
            
            logger.info(f"✅ Found {len(insights)} insights with review status: {status}")
            return insights
            
        except Exception as e:
            logger.error(f"❌ Error getting insights by review status: {e}")
            raise

    async def get_favorites_for_user(self, user_id: str, skip: int = 0, limit: int = 100) -> List[Insight]:
        """Get favorite insights for a user"""
        logger.info(f"Getting favorite insights for user: {user_id}")
        
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                return []
            
            cursor = db[self.collection_name].find({
                "user_id": user_id,
                "is_favorite": True,
                "is_archived": False
            }).skip(skip).limit(limit).sort("created_at", -1)
            
            insight_docs = await cursor.to_list(length=limit)
            
            insights = []
            for doc in insight_docs:
                # Convert ObjectId to string for Pydantic compatibility
                if "_id" in doc and doc["_id"]:
                    doc["_id"] = str(doc["_id"])
                insights.append(Insight(**doc))
            
            logger.info(f"✅ Found {len(insights)} favorite insights for user")
            return insights
            
        except Exception as e:
            logger.error(f"❌ Error getting favorite insights for user: {e}")
            raise

    async def get_archived_for_user(self, user_id: str, skip: int = 0, limit: int = 100) -> List[Insight]:
        """Get archived insights for a user"""
        logger.info(f"Getting archived insights for user: {user_id}")
        
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                return []
            
            cursor = db[self.collection_name].find({
                "user_id": user_id,
                "is_archived": True
            }).skip(skip).limit(limit).sort("archived_at", -1)
            
            insight_docs = await cursor.to_list(length=limit)
            
            insights = []
            for doc in insight_docs:
                # Convert ObjectId to string for Pydantic compatibility
                if "_id" in doc and doc["_id"]:
                    doc["_id"] = str(doc["_id"])
                insights.append(Insight(**doc))
            
            logger.info(f"✅ Found {len(insights)} archived insights for user")
            return insights
            
        except Exception as e:
            logger.error(f"❌ Error getting archived insights for user: {e}")
            raise

    async def get_actionable_for_user(self, user_id: str, skip: int = 0, limit: int = 100) -> List[Insight]:
        """Get actionable insights for a user"""
        logger.info(f"Getting actionable insights for user: {user_id}")
        
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                return []
            
            cursor = db[self.collection_name].find({
                "user_id": user_id,
                "is_actionable": True,
                "is_archived": False
            }).skip(skip).limit(limit).sort("created_at", -1)
            
            insight_docs = await cursor.to_list(length=limit)
            
            insights = []
            for doc in insight_docs:
                # Convert ObjectId to string for Pydantic compatibility
                if "_id" in doc and doc["_id"]:
                    doc["_id"] = str(doc["_id"])
                insights.append(Insight(**doc))
            
            logger.info(f"✅ Found {len(insights)} actionable insights for user")
            return insights
            
        except Exception as e:
            logger.error(f"❌ Error getting actionable insights for user: {e}")
            raise

    async def search_insights(self, user_id: str, query: str, skip: int = 0, limit: int = 100) -> List[Insight]:
        """Search insights by text content"""
        logger.info(f"Searching insights for user: {user_id} with query: {query}")
        
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                return []
            
            # Create text search query
            search_filter = {
                "user_id": user_id,
                "$or": [
                    {"title": {"$regex": query, "$options": "i"}},
                    {"content": {"$regex": query, "$options": "i"}},
                    {"summary": {"$regex": query, "$options": "i"}},
                    {"tags": {"$regex": query, "$options": "i"}}
                ]
            }
            
            cursor = db[self.collection_name].find(search_filter).skip(skip).limit(limit).sort("created_at", -1)
            insight_docs = await cursor.to_list(length=limit)
            
            insights = []
            for doc in insight_docs:
                # Convert ObjectId to string for Pydantic compatibility
                if "_id" in doc and doc["_id"]:
                    doc["_id"] = str(doc["_id"])
                insights.append(Insight(**doc))
            
            logger.info(f"✅ Found {len(insights)} insights matching search query")
            return insights
            
        except Exception as e:
            logger.error(f"❌ Error searching insights: {e}")
            raise

    async def update(self, insight_id: str, update_data: Dict[str, Any]) -> Optional[Insight]:
        """Update an insight"""
        logger.info(f"Updating insight: {insight_id}")
        
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                return None
            
            # Add updated_at timestamp
            update_data["updated_at"] = datetime.utcnow()
            
            result = await db[self.collection_name].update_one(
                {"_id": ObjectId(insight_id)},
                {"$set": update_data}
            )
            
            if result.modified_count:
                updated_insight = await self.get_by_id(insight_id)
                logger.info(f"✅ Successfully updated insight: {insight_id}")
                return updated_insight
            
            logger.warning(f"No insight found to update with ID: {insight_id}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error updating insight: {e}")
            raise

    async def delete(self, insight_id: str) -> bool:
        """Delete an insight"""
        logger.info(f"Deleting insight: {insight_id}")
        
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                return False
            
            result = await db[self.collection_name].delete_one({"_id": ObjectId(insight_id)})
            
            if result.deleted_count > 0:
                logger.info(f"✅ Successfully deleted insight: {insight_id}")
                return True
            
            logger.warning(f"No insight found to delete with ID: {insight_id}")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error deleting insight: {e}")
            raise

    async def increment_view_count(self, insight_id: str) -> Optional[Insight]:
        """Increment view count for an insight"""
        logger.info(f"Incrementing view count for insight: {insight_id}")
        
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                return None
            
            result = await db[self.collection_name].update_one(
                {"_id": ObjectId(insight_id)},
                {
                    "$inc": {"view_count": 1},
                    "$set": {
                        "last_viewed_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            if result.modified_count:
                updated_insight = await self.get_by_id(insight_id)
                logger.info(f"✅ Successfully incremented view count for insight")
                return updated_insight
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error incrementing view count: {e}")
            raise

    async def mark_as_favorite(self, insight_id: str) -> Optional[Insight]:
        """Mark insight as favorite"""
        logger.info(f"Marking insight as favorite: {insight_id}")
        
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                return None
            
            result = await db[self.collection_name].update_one(
                {"_id": ObjectId(insight_id)},
                {
                    "$set": {
                        "is_favorite": True,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            if result.modified_count:
                updated_insight = await self.get_by_id(insight_id)
                logger.info(f"✅ Successfully marked insight as favorite")
                return updated_insight
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error marking insight as favorite: {e}")
            raise

    async def remove_from_favorites(self, insight_id: str) -> Optional[Insight]:
        """Remove insight from favorites"""
        logger.info(f"Removing insight from favorites: {insight_id}")
        
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                return None
            
            result = await db[self.collection_name].update_one(
                {"_id": ObjectId(insight_id)},
                {
                    "$set": {
                        "is_favorite": False,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            if result.modified_count:
                updated_insight = await self.get_by_id(insight_id)
                logger.info(f"✅ Successfully removed insight from favorites")
                return updated_insight
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error removing insight from favorites: {e}")
            raise

    async def archive_insight(self, insight_id: str) -> Optional[Insight]:
        """Archive an insight"""
        logger.info(f"Archiving insight: {insight_id}")
        
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                return None
            
            result = await db[self.collection_name].update_one(
                {"_id": ObjectId(insight_id)},
                {
                    "$set": {
                        "is_archived": True,
                        "archived_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            if result.modified_count:
                updated_insight = await self.get_by_id(insight_id)
                logger.info(f"✅ Successfully archived insight")
                return updated_insight
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error archiving insight: {e}")
            raise

    async def unarchive_insight(self, insight_id: str) -> Optional[Insight]:
        """Unarchive an insight"""
        logger.info(f"Unarchiving insight: {insight_id}")
        
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                return None
            
            result = await db[self.collection_name].update_one(
                {"_id": ObjectId(insight_id)},
                {
                    "$set": {
                        "is_archived": False,
                        "updated_at": datetime.utcnow()
                    },
                    "$unset": {"archived_at": ""}
                }
            )
            
            if result.modified_count:
                updated_insight = await self.get_by_id(insight_id)
                logger.info(f"✅ Successfully unarchived insight")
                return updated_insight
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error unarchiving insight: {e}")
            raise

    async def count_for_user(self, user_id: str) -> int:
        """Count total insights for a user"""
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                return 0
            
            count = await db[self.collection_name].count_documents({"user_id": user_id})
            return count
            
        except Exception as e:
            logger.error(f"❌ Error counting insights for user: {e}")
            raise

    async def count_by_category_for_user(self, user_id: str, category: CategoryType) -> int:
        """Count insights by category for a user"""
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                return 0
            
            count = await db[self.collection_name].count_documents({
                "user_id": user_id,
                "$or": [
                    {"category": category},
                    {"subcategories": category}
                ]
            })
            return count
            
        except Exception as e:
            logger.error(f"❌ Error counting insights by category for user: {e}")
            raise