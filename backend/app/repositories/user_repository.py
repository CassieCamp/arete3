from typing import Optional
from bson import ObjectId
from app.models.user import User
from app.db.mongodb import get_database


class UserRepository:
    def __init__(self):
        self.collection_name = "users"

    async def create_user(self, user: User) -> User:
        """Create a new user"""
        db = get_database()
        user_dict = user.dict(by_alias=True, exclude_unset=True)
        
        # Remove the id field if it's None or empty
        if "_id" in user_dict and user_dict["_id"] is None:
            del user_dict["_id"]
            
        result = await db[self.collection_name].insert_one(user_dict)
        user.id = result.inserted_id
        return user

    async def get_user_by_clerk_id(self, clerk_user_id: str) -> Optional[User]:
        """Get user by Clerk user ID"""
        db = get_database()
        user_doc = await db[self.collection_name].find_one({"clerk_user_id": clerk_user_id})
        
        if user_doc:
            return User(**user_doc)
        return None

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        db = get_database()
        user_doc = await db[self.collection_name].find_one({"_id": ObjectId(user_id)})
        
        if user_doc:
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