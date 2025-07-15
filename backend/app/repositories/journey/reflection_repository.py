from typing import Optional, List, Dict, Any
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db.mongodb import get_database
from app.models.journey.reflection import ReflectionSource

class ReflectionSourceRepository:
    """Repository for managing reflection sources in MongoDB."""

    def __init__(self):
        """Initialize repository with database connection and collection."""
        self.db = get_database()
        self.collection_name = ReflectionSource.Config.collection_name

    async def create(self, reflection_source: ReflectionSource) -> ReflectionSource:
        """Create a new reflection source."""
        reflection_dict = reflection_source.model_dump(by_alias=True, exclude_unset=True)
        if "_id" in reflection_dict and reflection_dict["_id"] is None:
            del reflection_dict["_id"]
        
        result = await self.db[self.collection_name].insert_one(reflection_dict)
        reflection_source.id = str(result.inserted_id)
        return reflection_source

    async def get_by_id(self, id: str) -> Optional[ReflectionSource]:
        """Get a reflection source by its ID."""
        try:
            doc = await self.db[self.collection_name].find_one({"_id": ObjectId(id)})
            if doc:
                doc["_id"] = str(doc["_id"])
                return ReflectionSource(**doc)
            return None
        except Exception:
            return None

    async def get_by_user_id(self, user_id: str) -> List[ReflectionSource]:
        """Get all reflection sources for a given user_id."""
        cursor = self.db[self.collection_name].find({"user_id": user_id}).sort("created_at", -1)
        docs = await cursor.to_list(length=None)
        # Convert ObjectId to string for each document
        for doc in docs:
            if "_id" in doc:
                doc["_id"] = str(doc["_id"])
        return [ReflectionSource(**doc) for doc in docs]

    async def update(self, id: str, reflection_source_update: dict) -> Optional[ReflectionSource]:
        """Update a reflection source by its ID using the provided dictionary of update fields."""
        try:
            # Add updated_at timestamp
            from datetime import datetime
            reflection_source_update["updated_at"] = datetime.utcnow()
            
            result = await self.db[self.collection_name].update_one(
                {"_id": ObjectId(id)},
                {"$set": reflection_source_update}
            )
            if result.modified_count:
                return await self.get_by_id(id)
            return None
        except Exception:
            return None

    async def delete(self, id: str) -> bool:
        """Delete a reflection source by its ID and return True if successful, False otherwise."""
        try:
            result = await self.db[self.collection_name].delete_one({"_id": ObjectId(id)})
            return result.deleted_count > 0
        except Exception:
            return False

    async def get_all_for_user(self, user_id: str, skip: int = 0, limit: int = 100) -> List[ReflectionSource]:
        """Get all reflection sources for a user with pagination."""
        cursor = self.db[self.collection_name].find({"user_id": user_id}).skip(skip).limit(limit).sort("created_at", -1)
        docs = await cursor.to_list(length=limit)
        # Convert ObjectId to string for each document
        for doc in docs:
            if "_id" in doc:
                doc["_id"] = str(doc["_id"])
        return [ReflectionSource(**doc) for doc in docs]

    async def add_insight_id(self, reflection_id: str, insight_id: str) -> Optional[ReflectionSource]:
        """Add an insight ID to a reflection's insight_ids list."""
        try:
            result = await self.db[self.collection_name].update_one(
                {"_id": ObjectId(reflection_id)},
                {"$addToSet": {"insight_ids": insight_id}}
            )
            if result.modified_count:
                return await self.get_by_id(reflection_id)
            return None
        except Exception:
            return None

    async def get_by_category(self, user_id: str, category, skip: int = 0, limit: int = 100) -> List[ReflectionSource]:
        """Get reflection sources by category for a user."""
        cursor = self.db[self.collection_name].find({
            "user_id": user_id,
            "categories": category
        }).skip(skip).limit(limit).sort("created_at", -1)
        docs = await cursor.to_list(length=limit)
        # Convert ObjectId to string for each document
        for doc in docs:
            if "_id" in doc:
                doc["_id"] = str(doc["_id"])
        return [ReflectionSource(**doc) for doc in docs]

    async def count_for_user(self, user_id: str) -> int:
        """Count total reflection sources for a user."""
        try:
            return await self.db[self.collection_name].count_documents({"user_id": user_id})
        except Exception:
            return 0