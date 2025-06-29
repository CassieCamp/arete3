from typing import Optional, List
from bson import ObjectId
from datetime import datetime
from app.models.coaching_relationship import CoachingRelationship, RelationshipStatus
from app.db.mongodb import get_database
import logging

logger = logging.getLogger(__name__)


class CoachingRelationshipRepository:
    def __init__(self):
        self.collection_name = "coaching_relationships"

    async def create_relationship(self, relationship: CoachingRelationship) -> CoachingRelationship:
        """Create a new coaching relationship (connection request)"""
        logger.info(f"=== CoachingRelationshipRepository.create_relationship called ===")
        logger.info(f"Input relationship: {relationship}")
        
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                raise Exception("Database connection is None")
            
            relationship_dict = relationship.dict(by_alias=True, exclude_unset=True)
            logger.info(f"Relationship dict before processing: {relationship_dict}")
            
            # Remove the id field if it's None or empty
            if "_id" in relationship_dict and relationship_dict["_id"] is None:
                del relationship_dict["_id"]
                logger.info("Removed None _id field")
            
            # Ensure timestamps are set
            now = datetime.utcnow()
            relationship_dict["created_at"] = now
            relationship_dict["updated_at"] = now
            
            logger.info(f"Final relationship dict for insertion: {relationship_dict}")
            
            result = await db[self.collection_name].insert_one(relationship_dict)
            logger.info(f"Insert result: {result}")
            logger.info(f"Inserted ID: {result.inserted_id}")
            
            relationship.id = result.inserted_id
            logger.info(f"✅ Successfully created coaching relationship with ID: {relationship.id}")
            return relationship
            
        except Exception as e:
            logger.error(f"❌ Error in create_relationship: {e}")
            logger.error(f"Exception type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    async def get_relationship_by_id(self, relationship_id: str) -> Optional[CoachingRelationship]:
        """Get coaching relationship by ID"""
        logger.info(f"=== CoachingRelationshipRepository.get_relationship_by_id called ===")
        logger.info(f"Searching for relationship_id: {relationship_id}")
        
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                raise Exception("Database connection is None")
            
            relationship_doc = await db[self.collection_name].find_one({"_id": ObjectId(relationship_id)})
            logger.info(f"Query result: {relationship_doc}")
            
            if relationship_doc:
                # Convert ObjectId to string for Pydantic compatibility
                if "_id" in relationship_doc and relationship_doc["_id"]:
                    relationship_doc["_id"] = str(relationship_doc["_id"])
                    logger.info(f"Converted ObjectId to string: {relationship_doc['_id']}")
                
                relationship = CoachingRelationship(**relationship_doc)
                logger.info(f"✅ Found coaching relationship: {relationship}")
                return relationship
            
            logger.info("No coaching relationship found with that ID")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error in get_relationship_by_id: {e}")
            logger.error(f"Exception type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    async def update_relationship_status(self, relationship_id: str, status: RelationshipStatus) -> Optional[CoachingRelationship]:
        """Update the status of a coaching relationship"""
        logger.info(f"=== CoachingRelationshipRepository.update_relationship_status called ===")
        logger.info(f"Updating relationship_id: {relationship_id} to status: {status}")
        
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                raise Exception("Database connection is None")
            
            update_data = {
                "status": status.value,
                "updated_at": datetime.utcnow()
            }
            
            result = await db[self.collection_name].update_one(
                {"_id": ObjectId(relationship_id)},
                {"$set": update_data}
            )
            
            logger.info(f"Update result: modified_count={result.modified_count}")
            
            if result.modified_count:
                updated_relationship = await self.get_relationship_by_id(relationship_id)
                logger.info(f"✅ Successfully updated relationship status")
                return updated_relationship
            
            logger.info("No relationship was updated")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error in update_relationship_status: {e}")
            logger.error(f"Exception type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    async def get_pending_requests_for_user(self, user_id: str) -> List[CoachingRelationship]:
        """Get all pending connection requests for a user where they are the client"""
        logger.info(f"=== CoachingRelationshipRepository.get_pending_requests_for_user called ===")
        logger.info(f"Searching for pending requests for user_id: {user_id}")
        
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                raise Exception("Database connection is None")
            
            # Find relationships where user is the client and status is pending_by_coach
            query = {
                "client_user_id": user_id,
                "status": RelationshipStatus.PENDING_BY_COACH.value
            }
            
            logger.info(f"Query: {query}")
            
            cursor = db[self.collection_name].find(query)
            relationship_docs = await cursor.to_list(length=None)
            
            logger.info(f"Found {len(relationship_docs)} pending requests")
            
            relationships = []
            for doc in relationship_docs:
                # Convert ObjectId to string for Pydantic compatibility
                if "_id" in doc and doc["_id"]:
                    doc["_id"] = str(doc["_id"])
                relationships.append(CoachingRelationship(**doc))
            
            logger.info(f"✅ Successfully retrieved {len(relationships)} pending requests")
            return relationships
            
        except Exception as e:
            logger.error(f"❌ Error in get_pending_requests_for_user: {e}")
            logger.error(f"Exception type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    async def get_active_relationships_for_user(self, user_id: str) -> List[CoachingRelationship]:
        """Get all active coaching relationships for a user (as coach or client)"""
        logger.info(f"=== CoachingRelationshipRepository.get_active_relationships_for_user called ===")
        logger.info(f"Searching for active relationships for user_id: {user_id}")
        
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                raise Exception("Database connection is None")
            
            # Find relationships where user is either coach or client and status is active
            query = {
                "$and": [
                    {"status": RelationshipStatus.ACTIVE.value},
                    {"$or": [
                        {"coach_user_id": user_id},
                        {"client_user_id": user_id}
                    ]}
                ]
            }
            
            logger.info(f"Query: {query}")
            
            cursor = db[self.collection_name].find(query)
            relationship_docs = await cursor.to_list(length=None)
            
            logger.info(f"Found {len(relationship_docs)} active relationships")
            
            relationships = []
            for doc in relationship_docs:
                # Convert ObjectId to string for Pydantic compatibility
                if "_id" in doc and doc["_id"]:
                    doc["_id"] = str(doc["_id"])
                relationships.append(CoachingRelationship(**doc))
            
            logger.info(f"✅ Successfully retrieved {len(relationships)} active relationships")
            return relationships
            
        except Exception as e:
            logger.error(f"❌ Error in get_active_relationships_for_user: {e}")
            logger.error(f"Exception type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    async def get_relationship_between_users(self, coach_user_id: str, client_user_id: str) -> Optional[CoachingRelationship]:
        """Get coaching relationship between specific coach and client"""
        logger.info(f"=== CoachingRelationshipRepository.get_relationship_between_users called ===")
        logger.info(f"Searching for relationship between coach: {coach_user_id} and client: {client_user_id}")
        
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                raise Exception("Database connection is None")
            
            query = {
                "coach_user_id": coach_user_id,
                "client_user_id": client_user_id
            }
            
            relationship_doc = await db[self.collection_name].find_one(query)
            logger.info(f"Query result: {relationship_doc}")
            
            if relationship_doc:
                # Convert ObjectId to string for Pydantic compatibility
                if "_id" in relationship_doc and relationship_doc["_id"]:
                    relationship_doc["_id"] = str(relationship_doc["_id"])
                
                relationship = CoachingRelationship(**relationship_doc)
                logger.info(f"✅ Found relationship between users")
                return relationship
            
            logger.info("No relationship found between these users")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error in get_relationship_between_users: {e}")
            logger.error(f"Exception type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    async def delete_relationship(self, relationship_id: str) -> bool:
        """Delete a coaching relationship"""
        logger.info(f"=== CoachingRelationshipRepository.delete_relationship called ===")
        logger.info(f"Deleting relationship_id: {relationship_id}")
        
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                raise Exception("Database connection is None")
            
            result = await db[self.collection_name].delete_one({"_id": ObjectId(relationship_id)})
            
            success = result.deleted_count > 0
            logger.info(f"Delete result: deleted_count={result.deleted_count}, success={success}")
            
            if success:
                logger.info(f"✅ Successfully deleted coaching relationship")
            else:
                logger.info("No relationship was deleted")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error in delete_relationship: {e}")
            logger.error(f"Exception type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise