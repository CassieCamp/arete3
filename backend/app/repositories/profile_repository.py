from typing import Optional
from bson import ObjectId
from datetime import datetime
from app.models.profile import Profile
from app.db.mongodb import get_database


class ProfileRepository:
    def __init__(self):
        self.collection_name = "profiles"

    async def create_profile(self, profile: Profile) -> Profile:
        """Create a new profile"""
        db = get_database()
        # FIX: Use model_dump() instead of deprecated dict() method for Pydantic v2
        profile_dict = profile.model_dump(by_alias=True, exclude_unset=True)
        
        # Remove the id field if it's None or empty
        if "_id" in profile_dict and profile_dict["_id"] is None:
            del profile_dict["_id"]
            
        result = await db[self.collection_name].insert_one(profile_dict)
        profile.id = result.inserted_id
        return profile

    async def get_profile_by_user_id(self, user_id: str) -> Optional[Profile]:
        """Get profile by user ID"""
        db = get_database()
        profile_doc = await db[self.collection_name].find_one({"user_id": user_id})
        
        if profile_doc:
            return Profile(**profile_doc)
        return None

    async def get_profile_by_clerk_id(self, clerk_user_id: str) -> Optional[Profile]:
        """Get profile by Clerk user ID"""
        db = get_database()
        profile_doc = await db[self.collection_name].find_one({"clerk_user_id": clerk_user_id})
        
        if profile_doc:
            # Convert ObjectId to string for Pydantic compatibility
            if "_id" in profile_doc and profile_doc["_id"]:
                profile_doc["_id"] = str(profile_doc["_id"])
            return Profile(**profile_doc)
        return None

    async def get_profile_by_id(self, profile_id: str) -> Optional[Profile]:
        """Get profile by ID"""
        db = get_database()
        profile_doc = await db[self.collection_name].find_one({"_id": ObjectId(profile_id)})
        
        if profile_doc:
            return Profile(**profile_doc)
        return None

    async def update_profile(self, user_id: str, update_data: dict) -> Optional[Profile]:
        """Update profile by clerk_user_id (not user_id)"""
        db = get_database()
        
        # Add updated_at timestamp
        update_data["updated_at"] = datetime.utcnow()
        
        # FIX: Update by clerk_user_id instead of user_id to match how profiles are queried
        result = await db[self.collection_name].update_one(
            {"clerk_user_id": user_id},
            {"$set": update_data}
        )
        
        if result.modified_count:
            return await self.get_profile_by_clerk_id(user_id)
        return None

    async def delete_profile(self, user_id: str) -> bool:
        """Delete profile by user ID"""
        db = get_database()
        result = await db[self.collection_name].delete_one({"user_id": user_id})
        return result.deleted_count > 0

    async def profile_exists(self, user_id: str) -> bool:
        """Check if profile exists for user"""
        db = get_database()
        count = await db[self.collection_name].count_documents({"user_id": user_id})
        return count > 0