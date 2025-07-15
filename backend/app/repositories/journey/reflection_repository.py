"""
Journey System Reflection Repository

This module contains the repository class for managing reflection sources in MongoDB.
"""

from typing import Optional, List, Dict, Any
from bson import ObjectId
from datetime import datetime
import logging

from app.models.journey.reflection import ReflectionSource, ProcessingEvent
from app.models.journey.enums import ProcessingStatus, CategoryType
from app.db.mongodb import get_database

logger = logging.getLogger(__name__)


class ReflectionRepository:
    """Repository for managing reflection sources and processing events"""
    
    def __init__(self):
        self.collection_name = "journey_reflections"
        self.events_collection_name = "journey_processing_events"

    async def create(self, reflection: ReflectionSource) -> ReflectionSource:
        """Create a new reflection source"""
        logger.info(f"Creating new reflection source: {reflection.title}")
        
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                raise Exception("Database connection is None")
            
            reflection_dict = reflection.model_dump(by_alias=True, exclude_unset=True)
            
            # Remove the id field if it's None or empty
            if "_id" in reflection_dict and reflection_dict["_id"] is None:
                del reflection_dict["_id"]
            
            result = await db[self.collection_name].insert_one(reflection_dict)
            reflection.id = result.inserted_id
            
            logger.info(f"✅ Successfully created reflection source with ID: {reflection.id}")
            return reflection
            
        except Exception as e:
            logger.error(f"❌ Error creating reflection source: {e}")
            raise

    async def get_by_id(self, reflection_id: str) -> Optional[ReflectionSource]:
        """Get reflection source by ID"""
        logger.info(f"Getting reflection source by ID: {reflection_id}")
        
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                return None
            
            reflection_doc = await db[self.collection_name].find_one({"_id": ObjectId(reflection_id)})
            
            if reflection_doc:
                # Convert ObjectId to string for Pydantic compatibility
                if "_id" in reflection_doc and reflection_doc["_id"]:
                    reflection_doc["_id"] = str(reflection_doc["_id"])
                
                reflection = ReflectionSource(**reflection_doc)
                logger.info(f"✅ Found reflection source: {reflection.title}")
                return reflection
            
            logger.info("No reflection source found with that ID")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting reflection source by ID: {e}")
            raise

    async def get_all_for_user(self, user_id: str, skip: int = 0, limit: int = 100) -> List[ReflectionSource]:
        """Get all reflection sources for a user with pagination"""
        logger.info(f"Getting reflection sources for user: {user_id} (skip={skip}, limit={limit})")
        
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                return []
            
            cursor = db[self.collection_name].find({"user_id": user_id}).skip(skip).limit(limit).sort("created_at", -1)
            reflection_docs = await cursor.to_list(length=limit)
            
            reflections = []
            for doc in reflection_docs:
                # Convert ObjectId to string for Pydantic compatibility
                if "_id" in doc and doc["_id"]:
                    doc["_id"] = str(doc["_id"])
                reflections.append(ReflectionSource(**doc))
            
            logger.info(f"✅ Found {len(reflections)} reflection sources for user")
            return reflections
            
        except Exception as e:
            logger.error(f"❌ Error getting reflection sources for user: {e}")
            raise

    async def get_by_category(self, user_id: str, category: CategoryType, skip: int = 0, limit: int = 100) -> List[ReflectionSource]:
        """Get reflection sources by category for a user"""
        logger.info(f"Getting reflection sources by category: {category} for user: {user_id}")
        
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                return []
            
            cursor = db[self.collection_name].find({
                "user_id": user_id,
                "categories": category
            }).skip(skip).limit(limit).sort("created_at", -1)
            
            reflection_docs = await cursor.to_list(length=limit)
            
            reflections = []
            for doc in reflection_docs:
                # Convert ObjectId to string for Pydantic compatibility
                if "_id" in doc and doc["_id"]:
                    doc["_id"] = str(doc["_id"])
                reflections.append(ReflectionSource(**doc))
            
            logger.info(f"✅ Found {len(reflections)} reflection sources for category: {category}")
            return reflections
            
        except Exception as e:
            logger.error(f"❌ Error getting reflection sources by category: {e}")
            raise

    async def get_by_processing_status(self, user_id: str, status: str, skip: int = 0, limit: int = 100) -> List[ReflectionSource]:
        """Get reflection sources by processing status for a user"""
        logger.info(f"Getting reflection sources by processing status: {status} for user: {user_id}")
        
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                return []
            
            cursor = db[self.collection_name].find({
                "user_id": user_id,
                "processing_status": status
            }).skip(skip).limit(limit).sort("created_at", -1)
            
            reflection_docs = await cursor.to_list(length=limit)
            
            reflections = []
            for doc in reflection_docs:
                # Convert ObjectId to string for Pydantic compatibility
                if "_id" in doc and doc["_id"]:
                    doc["_id"] = str(doc["_id"])
                reflections.append(ReflectionSource(**doc))
            
            logger.info(f"✅ Found {len(reflections)} reflection sources with status: {status}")
            return reflections
            
        except Exception as e:
            logger.error(f"❌ Error getting reflection sources by processing status: {e}")
            raise

    async def update(self, reflection_id: str, update_data: Dict[str, Any]) -> Optional[ReflectionSource]:
        """Update a reflection source"""
        logger.info(f"Updating reflection source: {reflection_id}")
        
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                return None
            
            # Add updated_at timestamp
            update_data["updated_at"] = datetime.utcnow()
            
            result = await db[self.collection_name].update_one(
                {"_id": ObjectId(reflection_id)},
                {"$set": update_data}
            )
            
            if result.modified_count:
                updated_reflection = await self.get_by_id(reflection_id)
                logger.info(f"✅ Successfully updated reflection source: {reflection_id}")
                return updated_reflection
            
            logger.warning(f"No reflection source found to update with ID: {reflection_id}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error updating reflection source: {e}")
            raise

    async def delete(self, reflection_id: str) -> bool:
        """Delete a reflection source"""
        logger.info(f"Deleting reflection source: {reflection_id}")
        
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                return False
            
            result = await db[self.collection_name].delete_one({"_id": ObjectId(reflection_id)})
            
            if result.deleted_count > 0:
                logger.info(f"✅ Successfully deleted reflection source: {reflection_id}")
                return True
            
            logger.warning(f"No reflection source found to delete with ID: {reflection_id}")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error deleting reflection source: {e}")
            raise

    async def add_insight_id(self, reflection_id: str, insight_id: str) -> Optional[ReflectionSource]:
        """Add an insight ID to a reflection source"""
        logger.info(f"Adding insight ID {insight_id} to reflection {reflection_id}")
        
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                return None
            
            result = await db[self.collection_name].update_one(
                {"_id": ObjectId(reflection_id)},
                {
                    "$addToSet": {"insight_ids": insight_id},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            
            if result.modified_count:
                updated_reflection = await self.get_by_id(reflection_id)
                logger.info(f"✅ Successfully added insight ID to reflection source")
                return updated_reflection
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error adding insight ID to reflection source: {e}")
            raise

    async def count_for_user(self, user_id: str) -> int:
        """Count total reflection sources for a user"""
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                return 0
            
            count = await db[self.collection_name].count_documents({"user_id": user_id})
            return count
            
        except Exception as e:
            logger.error(f"❌ Error counting reflection sources for user: {e}")
            raise

    # Processing Events Methods
    async def create_processing_event(self, event: ProcessingEvent) -> ProcessingEvent:
        """Create a new processing event"""
        logger.info(f"Creating processing event: {event.event_type}")
        
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                raise Exception("Database connection is None")
            
            event_dict = event.model_dump(by_alias=True, exclude_unset=True)
            
            # Remove the id field if it's None or empty
            if "_id" in event_dict and event_dict["_id"] is None:
                del event_dict["_id"]
            
            result = await db[self.events_collection_name].insert_one(event_dict)
            event.id = result.inserted_id
            
            logger.info(f"✅ Successfully created processing event with ID: {event.id}")
            return event
            
        except Exception as e:
            logger.error(f"❌ Error creating processing event: {e}")
            raise

    async def get_processing_events_for_source(self, source_id: str) -> List[ProcessingEvent]:
        """Get all processing events for a reflection source"""
        logger.info(f"Getting processing events for source: {source_id}")
        
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                return []
            
            cursor = db[self.events_collection_name].find({"source_id": source_id}).sort("created_at", -1)
            event_docs = await cursor.to_list(length=None)
            
            events = []
            for doc in event_docs:
                # Convert ObjectId to string for Pydantic compatibility
                if "_id" in doc and doc["_id"]:
                    doc["_id"] = str(doc["_id"])
                events.append(ProcessingEvent(**doc))
            
            logger.info(f"✅ Found {len(events)} processing events for source")
            return events
            
        except Exception as e:
            logger.error(f"❌ Error getting processing events for source: {e}")
            raise