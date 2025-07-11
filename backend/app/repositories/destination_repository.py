from typing import Optional, List
from bson import ObjectId
from datetime import datetime
from app.models.destination import Destination
from app.db.mongodb import get_database
import logging

logger = logging.getLogger(__name__)


class DestinationRepository:
    def __init__(self):
        self.collection_name = "destinations"

    async def create_destination(self, destination: Destination) -> Destination:
        """Create a new destination"""
        logger.info(f"=== DestinationRepository.create_destination called ===")
        logger.info(f"Input destination: {destination}")
        
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                raise Exception("Database connection is None")
            
            destination_dict = destination.model_dump(by_alias=True, exclude_unset=True)
            logger.info(f"Destination dict before processing: {destination_dict}")
            
            # Remove the id field if it's None or empty
            if "_id" in destination_dict and destination_dict["_id"] is None:
                del destination_dict["_id"]
                logger.info("Removed None _id field")
            
            # Ensure timestamps are set
            now = datetime.utcnow()
            destination_dict["created_at"] = now
            destination_dict["updated_at"] = now
            
            logger.info(f"Final destination dict for insertion: {destination_dict}")
            
            result = await db[self.collection_name].insert_one(destination_dict)
            logger.info(f"Insert result: {result}")
            logger.info(f"Inserted ID: {result.inserted_id}")
            
            destination.id = result.inserted_id
            logger.info(f"✅ Successfully created destination with ID: {destination.id}")
            return destination
            
        except Exception as e:
            logger.error(f"❌ Error in create_destination: {e}")
            logger.error(f"Exception type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    async def get_destination_by_id(self, destination_id: str) -> Optional[Destination]:
        """Get destination by ID"""
        logger.info(f"=== DestinationRepository.get_destination_by_id called ===")
        logger.info(f"Searching for destination_id: {destination_id}")
        
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                raise Exception("Database connection is None")
            
            destination_doc = await db[self.collection_name].find_one({"_id": ObjectId(destination_id)})
            logger.info(f"Query result: {destination_doc}")
            
            if destination_doc:
                # Convert ObjectId to string for Pydantic compatibility
                if "_id" in destination_doc and destination_doc["_id"]:
                    destination_doc["_id"] = str(destination_doc["_id"])
                    logger.info(f"Converted ObjectId to string: {destination_doc['_id']}")
                
                destination = Destination(**destination_doc)
                logger.info(f"✅ Found destination: {destination}")
                return destination
            
            logger.info("No destination found with that ID")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error in get_destination_by_id: {e}")
            logger.error(f"Exception type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    async def get_destinations_by_user_id(self, user_id: str) -> List[Destination]:
        """Get all destinations for a specific user"""
        logger.info(f"=== DestinationRepository.get_destinations_by_user_id called ===")
        logger.info(f"Searching for destinations for user_id: {user_id}")
        
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                raise Exception("Database connection is None")
            
            query = {"user_id": user_id}
            logger.info(f"Query: {query}")
            
            cursor = db[self.collection_name].find(query).sort("created_at", -1)  # Sort by newest first
            destination_docs = await cursor.to_list(length=None)
            
            logger.info(f"Found {len(destination_docs)} destinations for user")
            
            destinations = []
            for doc in destination_docs:
                # Convert ObjectId to string for Pydantic compatibility
                if "_id" in doc and doc["_id"]:
                    doc["_id"] = str(doc["_id"])
                destinations.append(Destination(**doc))
            
            logger.info(f"✅ Successfully retrieved {len(destinations)} destinations")
            return destinations
            
        except Exception as e:
            logger.error(f"❌ Error in get_destinations_by_user_id: {e}")
            logger.error(f"Exception type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    async def get_three_big_ideas(self, user_id: str) -> List[Destination]:
        """Get the three big ideas for a user, ordered by rank"""
        logger.info(f"=== DestinationRepository.get_three_big_ideas called ===")
        logger.info(f"Getting three big ideas for user_id: {user_id}")
        
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                raise Exception("Database connection is None")
            
            query = {"user_id": user_id, "is_big_idea": True}
            logger.info(f"Query: {query}")
            
            cursor = db[self.collection_name].find(query).sort("big_idea_rank", 1)  # Sort by rank ascending
            destination_docs = await cursor.to_list(length=3)  # Limit to 3
            
            logger.info(f"Found {len(destination_docs)} big ideas for user")
            
            destinations = []
            for doc in destination_docs:
                # Convert ObjectId to string for Pydantic compatibility
                if "_id" in doc and doc["_id"]:
                    doc["_id"] = str(doc["_id"])
                destinations.append(Destination(**doc))
            
            logger.info(f"✅ Successfully retrieved {len(destinations)} big ideas")
            return destinations
            
        except Exception as e:
            logger.error(f"❌ Error in get_three_big_ideas: {e}")
            logger.error(f"Exception type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    async def update_destination(self, destination_id: str, update_data: dict) -> Optional[Destination]:
        """Update an existing destination record"""
        logger.info(f"=== DestinationRepository.update_destination called ===")
        logger.info(f"Updating destination_id: {destination_id} with data: {update_data}")
        
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                raise Exception("Database connection is None")
            
            # Add updated_at timestamp
            update_data["updated_at"] = datetime.utcnow()
            
            result = await db[self.collection_name].update_one(
                {"_id": ObjectId(destination_id)},
                {"$set": update_data}
            )
            
            logger.info(f"Update result: modified_count={result.modified_count}")
            
            if result.modified_count:
                updated_destination = await self.get_destination_by_id(destination_id)
                logger.info(f"✅ Successfully updated destination")
                return updated_destination
            
            logger.info("No destination was updated")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error in update_destination: {e}")
            logger.error(f"Exception type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    async def delete_destination(self, destination_id: str) -> bool:
        """Delete a destination record from the database"""
        logger.info(f"=== DestinationRepository.delete_destination called ===")
        logger.info(f"Deleting destination_id: {destination_id}")
        
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                raise Exception("Database connection is None")
            
            result = await db[self.collection_name].delete_one({"_id": ObjectId(destination_id)})
            
            success = result.deleted_count > 0
            logger.info(f"Delete result: deleted_count={result.deleted_count}, success={success}")
            
            if success:
                logger.info(f"✅ Successfully deleted destination")
            else:
                logger.info("No destination was deleted")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error in delete_destination: {e}")
            logger.error(f"Exception type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    # Backward compatibility methods
    async def create_goal(self, goal_data: dict) -> Destination:
        """Backward compatibility wrapper for create_destination"""
        logger.info("Using backward compatibility wrapper: create_goal -> create_destination")
        
        # Convert goal_statement to destination_statement if present
        if "goal_statement" in goal_data:
            goal_data["destination_statement"] = goal_data.pop("goal_statement")
        
        destination = Destination(**goal_data)
        return await self.create_destination(destination)

    async def get_goal_by_id(self, goal_id: str) -> Optional[Destination]:
        """Backward compatibility wrapper for get_destination_by_id"""
        logger.info("Using backward compatibility wrapper: get_goal_by_id -> get_destination_by_id")
        return await self.get_destination_by_id(goal_id)

    async def get_goals_by_user_id(self, user_id: str) -> List[Destination]:
        """Backward compatibility wrapper for get_destinations_by_user_id"""
        logger.info("Using backward compatibility wrapper: get_goals_by_user_id -> get_destinations_by_user_id")
        return await self.get_destinations_by_user_id(user_id)

    async def update_goal(self, goal_id: str, update_data: dict) -> Optional[Destination]:
        """Backward compatibility wrapper for update_destination"""
        logger.info("Using backward compatibility wrapper: update_goal -> update_destination")
        
        # Convert goal_statement to destination_statement if present
        if "goal_statement" in update_data:
            update_data["destination_statement"] = update_data.pop("goal_statement")
        
        return await self.update_destination(goal_id, update_data)

    async def delete_goal(self, goal_id: str) -> bool:
        """Backward compatibility wrapper for delete_destination"""
        logger.info("Using backward compatibility wrapper: delete_goal -> delete_destination")
        return await self.delete_destination(goal_id)