from typing import List, Optional, Dict, Any
from app.models.small_step import SmallStep
from app.db.mongodb import get_database
from bson import ObjectId
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SmallStepRepository:
    def __init__(self):
        self.collection_name = "small_steps"

    async def create_small_step(self, small_step: SmallStep) -> SmallStep:
        """Create a new small step"""
        try:
            db = get_database()
            step_dict = small_step.model_dump(by_alias=True, exclude={"id"})
            
            # Remove the id field if it's None or empty
            if "_id" in step_dict and step_dict["_id"] is None:
                del step_dict["_id"]
            
            result = await db[self.collection_name].insert_one(step_dict)
            
            # Fetch the created small step
            created_step = await db[self.collection_name].find_one({"_id": result.inserted_id})
            
            # Convert ObjectId to string for Pydantic model
            if created_step and "_id" in created_step:
                created_step["_id"] = str(created_step["_id"])
            
            return SmallStep(**created_step)
            
        except Exception as e:
            logger.error(f"Error creating small step: {e}")
            raise

    async def get_small_step_by_id(self, step_id: str) -> Optional[SmallStep]:
        """Get small step by ID"""
        try:
            if not ObjectId.is_valid(step_id):
                return None
                
            db = get_database()
            step_data = await db[self.collection_name].find_one({"_id": ObjectId(step_id)})
            
            if step_data:
                # Convert ObjectId to string for Pydantic model
                step_data["_id"] = str(step_data["_id"])
                return SmallStep(**step_data)
            return None
            
        except Exception as e:
            logger.error(f"Error fetching small step {step_id}: {e}")
            return None

    async def get_small_steps_by_user(self, user_id: str, completed: Optional[bool] = None) -> List[SmallStep]:
        """Get small steps for a user, optionally filtered by completion status"""
        try:
            db = get_database()
            
            query = {"user_id": user_id}
            if completed is not None:
                query["completed"] = completed
            
            cursor = db[self.collection_name].find(query).sort("created_at", -1)
            
            steps = []
            async for step_data in cursor:
                # Convert ObjectId to string for Pydantic model
                if "_id" in step_data:
                    step_data["_id"] = str(step_data["_id"])
                steps.append(SmallStep(**step_data))
            
            return steps
            
        except Exception as e:
            logger.error(f"Error fetching small steps for user {user_id}: {e}")
            return []

    async def get_small_steps_by_entry(self, entry_id: str) -> List[SmallStep]:
        """Get small steps generated from a specific entry"""
        try:
            db = get_database()
            cursor = db[self.collection_name].find({"source_entry_id": entry_id}).sort("created_at", -1)
            
            steps = []
            async for step_data in cursor:
                # Convert ObjectId to string for Pydantic model
                if "_id" in step_data:
                    step_data["_id"] = str(step_data["_id"])
                steps.append(SmallStep(**step_data))
            
            return steps
            
        except Exception as e:
            logger.error(f"Error fetching small steps for entry {entry_id}: {e}")
            return []

    async def get_small_steps_by_destination(self, destination_id: str) -> List[SmallStep]:
        """Get small steps related to a specific destination"""
        try:
            db = get_database()
            cursor = db[self.collection_name].find({"related_destination_id": destination_id}).sort("created_at", -1)
            
            steps = []
            async for step_data in cursor:
                # Convert ObjectId to string for Pydantic model
                if "_id" in step_data:
                    step_data["_id"] = str(step_data["_id"])
                steps.append(SmallStep(**step_data))
            
            return steps
            
        except Exception as e:
            logger.error(f"Error fetching small steps for destination {destination_id}: {e}")
            return []

    async def update_small_step(self, step_id: str, update_data: Dict[str, Any]) -> Optional[SmallStep]:
        """Update small step"""
        try:
            if not ObjectId.is_valid(step_id):
                return None
            
            db = get_database()
            update_data["updated_at"] = datetime.utcnow()
            
            result = await db[self.collection_name].update_one(
                {"_id": ObjectId(step_id)},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                return await self.get_small_step_by_id(step_id)
            return None
            
        except Exception as e:
            logger.error(f"Error updating small step {step_id}: {e}")
            return None

    async def mark_completed(self, step_id: str, user_id: str) -> Optional[SmallStep]:
        """Mark a small step as completed"""
        try:
            if not ObjectId.is_valid(step_id):
                return None
            
            db = get_database()
            
            # Verify the step belongs to the user
            step = await self.get_small_step_by_id(step_id)
            if not step or step.user_id != user_id:
                return None
            
            update_data = {
                "completed": True,
                "completed_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            result = await db[self.collection_name].update_one(
                {"_id": ObjectId(step_id)},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                return await self.get_small_step_by_id(step_id)
            return None
            
        except Exception as e:
            logger.error(f"Error marking small step {step_id} as completed: {e}")
            return None

    async def mark_uncompleted(self, step_id: str, user_id: str) -> Optional[SmallStep]:
        """Mark a small step as not completed"""
        try:
            if not ObjectId.is_valid(step_id):
                return None
            
            db = get_database()
            
            # Verify the step belongs to the user
            step = await self.get_small_step_by_id(step_id)
            if not step or step.user_id != user_id:
                return None
            
            update_data = {
                "completed": False,
                "completed_at": None,
                "updated_at": datetime.utcnow()
            }
            
            result = await db[self.collection_name].update_one(
                {"_id": ObjectId(step_id)},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                return await self.get_small_step_by_id(step_id)
            return None
            
        except Exception as e:
            logger.error(f"Error marking small step {step_id} as uncompleted: {e}")
            return None

    async def delete_small_step(self, step_id: str) -> bool:
        """Delete small step"""
        try:
            if not ObjectId.is_valid(step_id):
                return False
                
            db = get_database()
            result = await db[self.collection_name].delete_one({"_id": ObjectId(step_id)})
            return result.deleted_count > 0
            
        except Exception as e:
            logger.error(f"Error deleting small step {step_id}: {e}")
            return False

    async def get_completion_stats(self, user_id: str) -> Dict[str, int]:
        """Get completion statistics for a user"""
        try:
            db = get_database()
            
            total_count = await db[self.collection_name].count_documents({"user_id": user_id})
            completed_count = await db[self.collection_name].count_documents({
                "user_id": user_id,
                "completed": True
            })
            
            return {
                "total": total_count,
                "completed": completed_count,
                "pending": total_count - completed_count
            }
            
        except Exception as e:
            logger.error(f"Error getting completion stats for user {user_id}: {e}")
            return {"total": 0, "completed": 0, "pending": 0}