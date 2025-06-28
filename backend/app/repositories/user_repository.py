from typing import Optional
from bson import ObjectId
from app.models.user import User
from app.db.mongodb import get_database
import logging

logger = logging.getLogger(__name__)


class UserRepository:
    def __init__(self):
        self.collection_name = "users"

    async def create_user(self, user: User) -> User:
        """Create a new user"""
        logger.info(f"=== UserRepository.create_user called ===")
        logger.info(f"Input user: {user}")
        
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                raise Exception("Database connection is None")
            
            logger.info(f"Database connection obtained: {db}")
            logger.info(f"Collection name: {self.collection_name}")
            
            user_dict = user.dict(by_alias=True, exclude_unset=True)
            logger.info(f"User dict before processing: {user_dict}")
            
            # Remove the id field if it's None or empty
            if "_id" in user_dict and user_dict["_id"] is None:
                del user_dict["_id"]
                logger.info("Removed None _id field")
            
            # Ensure email is stored in lowercase for consistent lookups
            if "email" in user_dict:
                original_email = user_dict["email"]
                user_dict["email"] = user_dict["email"].lower()
                logger.info(f"Email normalized: {original_email} -> {user_dict['email']}")
            
            logger.info(f"Final user dict for insertion: {user_dict}")
            
            logger.info("Attempting to insert user into database...")
            result = await db[self.collection_name].insert_one(user_dict)
            logger.info(f"Insert result: {result}")
            logger.info(f"Inserted ID: {result.inserted_id}")
            
            user.id = result.inserted_id
            logger.info(f"✅ Successfully created user with ID: {user.id}")
            return user
            
        except Exception as e:
            logger.error(f"❌ Error in create_user: {e}")
            logger.error(f"Exception type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    async def get_user_by_clerk_id(self, clerk_user_id: str) -> Optional[User]:
        """Get user by Clerk user ID"""
        logger.info(f"=== UserRepository.get_user_by_clerk_id called ===")
        logger.info(f"Searching for clerk_user_id: {clerk_user_id}")
        
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                raise Exception("Database connection is None")
            
            logger.info(f"Querying collection: {self.collection_name}")
            user_doc = await db[self.collection_name].find_one({"clerk_user_id": clerk_user_id})
            logger.info(f"Query result: {user_doc}")
            
            if user_doc:
                # Convert ObjectId to string for Pydantic compatibility
                if "_id" in user_doc and user_doc["_id"]:
                    user_doc["_id"] = str(user_doc["_id"])
                    logger.info(f"Converted ObjectId to string: {user_doc['_id']}")
                
                user = User(**user_doc)
                logger.info(f"✅ Found existing user: {user}")
                return user
            
            logger.info("No user found with that Clerk ID")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error in get_user_by_clerk_id: {e}")
            logger.error(f"Exception type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        db = get_database()
        user_doc = await db[self.collection_name].find_one({"email": email.lower()})
        
        if user_doc:
            # Convert ObjectId to string for Pydantic compatibility
            if "_id" in user_doc and user_doc["_id"]:
                user_doc["_id"] = str(user_doc["_id"])
            return User(**user_doc)
        return None

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        db = get_database()
        user_doc = await db[self.collection_name].find_one({"_id": ObjectId(user_id)})
        
        if user_doc:
            # Convert ObjectId to string for Pydantic compatibility
            if "_id" in user_doc and user_doc["_id"]:
                user_doc["_id"] = str(user_doc["_id"])
            return User(**user_doc)
        return None

    async def update_user(self, user_id: str, update_data: dict) -> Optional[User]:
        """Update user"""
        db = get_database()
        result = await db[self.collection_name].update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )
        
        if result.modified_count:
            return await self.get_user_by_id(user_id)
        return None

    async def delete_user(self, user_id: str) -> bool:
        """Delete user"""
        db = get_database()
        result = await db[self.collection_name].delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count > 0