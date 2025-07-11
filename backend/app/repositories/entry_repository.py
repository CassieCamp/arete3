from typing import List, Optional, Dict, Any
from app.models.entry import Entry
from app.db.mongodb import get_database
from bson import ObjectId
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class EntryRepository:
    def __init__(self):
        self.collection_name = "entries"

    async def create_entry(self, entry: Entry) -> Entry:
        """Create a new entry"""
        try:
            db = get_database()
            entry_dict = entry.model_dump(by_alias=True, exclude={"id"})
            
            # Remove the id field if it's None or empty
            if "_id" in entry_dict and entry_dict["_id"] is None:
                del entry_dict["_id"]
            
            result = await db[self.collection_name].insert_one(entry_dict)
            
            # Fetch the created entry
            created_entry = await db[self.collection_name].find_one({"_id": result.inserted_id})
            
            # Convert ObjectId to string for Pydantic model
            if created_entry and "_id" in created_entry:
                created_entry["_id"] = str(created_entry["_id"])
            
            return Entry(**created_entry)
            
        except Exception as e:
            logger.error(f"Error creating entry: {e}")
            raise

    async def get_entry_by_id(self, entry_id: str) -> Optional[Entry]:
        """Get entry by ID"""
        try:
            if not ObjectId.is_valid(entry_id):
                return None
                
            db = get_database()
            entry_data = await db[self.collection_name].find_one({"_id": ObjectId(entry_id)})
            
            if entry_data:
                # Convert ObjectId to string for Pydantic model
                entry_data["_id"] = str(entry_data["_id"])
                return Entry(**entry_data)
            return None
            
        except Exception as e:
            logger.error(f"Error fetching entry {entry_id}: {e}")
            return None

    async def get_entries_by_user(
        self,
        user_id: str,
        entry_type: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[Entry]:
        """Get entries for a user, optionally filtered by type"""
        try:
            db = get_database()
            
            # Build query
            query = {"client_user_id": user_id}
            if entry_type:
                query["entry_type"] = entry_type
            
            cursor = db[self.collection_name].find(query).sort("created_at", -1).skip(offset).limit(limit)
            
            entries = []
            async for entry_data in cursor:
                # Convert ObjectId to string for Pydantic model
                if "_id" in entry_data:
                    entry_data["_id"] = str(entry_data["_id"])
                entries.append(Entry(**entry_data))
            
            return entries
            
        except Exception as e:
            logger.error(f"Error fetching entries for user {user_id}: {e}")
            return []

    async def get_entries_by_relationship(
        self, 
        relationship_id: str,
        limit: int = 20,
        offset: int = 0
    ) -> List[Entry]:
        """Get entries for a coaching relationship"""
        try:
            db = get_database()
            cursor = db[self.collection_name].find(
                {"coaching_relationship_id": relationship_id}
            ).sort("session_date", -1).skip(offset).limit(limit)
            
            entries = []
            async for entry_data in cursor:
                # Convert ObjectId to string for Pydantic model
                if "_id" in entry_data:
                    entry_data["_id"] = str(entry_data["_id"])
                entries.append(Entry(**entry_data))
            
            return entries
            
        except Exception as e:
            logger.error(f"Error fetching entries for relationship {relationship_id}: {e}")
            return []

    async def update_entry(self, entry_id: str, update_data: Dict[str, Any]) -> Optional[Entry]:
        """Update entry"""
        try:
            if not ObjectId.is_valid(entry_id):
                return None
            
            db = get_database()
            update_data["updated_at"] = datetime.utcnow()
            
            result = await db[self.collection_name].update_one(
                {"_id": ObjectId(entry_id)},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                return await self.get_entry_by_id(entry_id)
            return None
            
        except Exception as e:
            logger.error(f"Error updating entry {entry_id}: {e}")
            return None

    async def delete_entry(self, entry_id: str) -> bool:
        """Delete entry"""
        try:
            if not ObjectId.is_valid(entry_id):
                return False
                
            db = get_database()
            result = await db[self.collection_name].delete_one({"_id": ObjectId(entry_id)})
            return result.deleted_count > 0
            
        except Exception as e:
            logger.error(f"Error deleting entry {entry_id}: {e}")
            return False

    async def get_entries_count_by_user(self, user_id: str, entry_type: Optional[str] = None) -> int:
        """Get total count of entries for a user"""
        try:
            db = get_database()
            query = {"client_user_id": user_id}
            if entry_type:
                query["entry_type"] = entry_type
            return await db[self.collection_name].count_documents(query)
        except Exception as e:
            logger.error(f"Error counting entries for user {user_id}: {e}")
            return 0

    async def accept_detected_goals(self, entry_id: str, accepted_goal_indices: List[int]) -> bool:
        """Mark detected goals as accepted"""
        try:
            if not ObjectId.is_valid(entry_id):
                return False
            
            db = get_database()
            
            # Get the entry first
            entry_data = await db[self.collection_name].find_one({"_id": ObjectId(entry_id)})
            if not entry_data:
                return False
            
            # Update the accepted status for specified goals
            detected_goals = entry_data.get("detected_goals", [])
            for i, goal in enumerate(detected_goals):
                if i in accepted_goal_indices:
                    goal["accepted"] = True
            
            # Update the entry
            result = await db[self.collection_name].update_one(
                {"_id": ObjectId(entry_id)},
                {"$set": {"detected_goals": detected_goals, "updated_at": datetime.utcnow()}}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error accepting detected goals for entry {entry_id}: {e}")
            return False