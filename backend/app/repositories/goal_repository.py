from typing import Optional, List
from bson import ObjectId
from datetime import datetime
from app.models.goal import Goal
from app.db.mongodb import get_database
import logging

logger = logging.getLogger(__name__)


class GoalRepository:
    def __init__(self):
        self.collection_name = "goals"

    async def create_goal(self, goal: Goal) -> Goal:
        """Create a new goal"""
        logger.info(f"=== GoalRepository.create_goal called ===")
        logger.info(f"Input goal: {goal}")
        
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                raise Exception("Database connection is None")
            
            goal_dict = goal.dict(by_alias=True, exclude_unset=True)
            logger.info(f"Goal dict before processing: {goal_dict}")
            
            # Remove the id field if it's None or empty
            if "_id" in goal_dict and goal_dict["_id"] is None:
                del goal_dict["_id"]
                logger.info("Removed None _id field")
            
            # Ensure timestamps are set
            now = datetime.utcnow()
            goal_dict["created_at"] = now
            goal_dict["updated_at"] = now
            
            logger.info(f"Final goal dict for insertion: {goal_dict}")
            
            result = await db[self.collection_name].insert_one(goal_dict)
            logger.info(f"Insert result: {result}")
            logger.info(f"Inserted ID: {result.inserted_id}")
            
            goal.id = result.inserted_id
            logger.info(f"✅ Successfully created goal with ID: {goal.id}")
            return goal
            
        except Exception as e:
            logger.error(f"❌ Error in create_goal: {e}")
            logger.error(f"Exception type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    async def get_goal_by_id(self, goal_id: str) -> Optional[Goal]:
        """Get goal by ID"""
        logger.info(f"=== GoalRepository.get_goal_by_id called ===")
        logger.info(f"Searching for goal_id: {goal_id}")
        
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                raise Exception("Database connection is None")
            
            goal_doc = await db[self.collection_name].find_one({"_id": ObjectId(goal_id)})
            logger.info(f"Query result: {goal_doc}")
            
            if goal_doc:
                # Convert ObjectId to string for Pydantic compatibility
                if "_id" in goal_doc and goal_doc["_id"]:
                    goal_doc["_id"] = str(goal_doc["_id"])
                    logger.info(f"Converted ObjectId to string: {goal_doc['_id']}")
                
                goal = Goal(**goal_doc)
                logger.info(f"✅ Found goal: {goal}")
                return goal
            
            logger.info("No goal found with that ID")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error in get_goal_by_id: {e}")
            logger.error(f"Exception type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    async def get_goals_by_user_id(self, user_id: str) -> List[Goal]:
        """Get all goals for a specific user"""
        logger.info(f"=== GoalRepository.get_goals_by_user_id called ===")
        logger.info(f"Searching for goals for user_id: {user_id}")
        
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                raise Exception("Database connection is None")
            
            query = {"user_id": user_id}
            logger.info(f"Query: {query}")
            
            cursor = db[self.collection_name].find(query).sort("created_at", -1)  # Sort by newest first
            goal_docs = await cursor.to_list(length=None)
            
            logger.info(f"Found {len(goal_docs)} goals for user")
            
            goals = []
            for doc in goal_docs:
                # Convert ObjectId to string for Pydantic compatibility
                if "_id" in doc and doc["_id"]:
                    doc["_id"] = str(doc["_id"])
                goals.append(Goal(**doc))
            
            logger.info(f"✅ Successfully retrieved {len(goals)} goals")
            return goals
            
        except Exception as e:
            logger.error(f"❌ Error in get_goals_by_user_id: {e}")
            logger.error(f"Exception type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    async def update_goal(self, goal_id: str, update_data: dict) -> Optional[Goal]:
        """Update an existing goal record"""
        logger.info(f"=== GoalRepository.update_goal called ===")
        logger.info(f"Updating goal_id: {goal_id} with data: {update_data}")
        
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                raise Exception("Database connection is None")
            
            # Add updated_at timestamp
            update_data["updated_at"] = datetime.utcnow()
            
            result = await db[self.collection_name].update_one(
                {"_id": ObjectId(goal_id)},
                {"$set": update_data}
            )
            
            logger.info(f"Update result: modified_count={result.modified_count}")
            
            if result.modified_count:
                updated_goal = await self.get_goal_by_id(goal_id)
                logger.info(f"✅ Successfully updated goal")
                return updated_goal
            
            logger.info("No goal was updated")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error in update_goal: {e}")
            logger.error(f"Exception type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    async def delete_goal(self, goal_id: str) -> bool:
        """Delete a goal record from the database"""
        logger.info(f"=== GoalRepository.delete_goal called ===")
        logger.info(f"Deleting goal_id: {goal_id}")
        
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                raise Exception("Database connection is None")
            
            result = await db[self.collection_name].delete_one({"_id": ObjectId(goal_id)})
            
            success = result.deleted_count > 0
            logger.info(f"Delete result: deleted_count={result.deleted_count}, success={success}")
            
            if success:
                logger.info(f"✅ Successfully deleted goal")
            else:
                logger.info("No goal was deleted")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error in delete_goal: {e}")
            logger.error(f"Exception type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise