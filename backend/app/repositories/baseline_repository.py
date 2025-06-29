from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorCollection
from app.db.mongodb import get_database
from app.models.client_baseline import ClientBaseline
from bson import ObjectId
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class BaselineRepository:
    def __init__(self):
        self.db = get_database()
        self.collection: AsyncIOMotorCollection = self.db.client_baselines
    
    async def create_baseline(self, baseline: ClientBaseline) -> ClientBaseline:
        """Create a new client baseline"""
        try:
            logger.info(f"=== BaselineRepository.create_baseline called ===")
            logger.info(f"Creating baseline for user_id: {baseline.user_id}")
            
            baseline_dict = baseline.model_dump(by_alias=True, exclude={"id"})
            result = await self.collection.insert_one(baseline_dict)
            
            baseline.id = result.inserted_id
            logger.info(f"✅ Created baseline with ID: {result.inserted_id}")
            return baseline
            
        except Exception as e:
            logger.error(f"❌ Error creating baseline: {e}")
            raise
    
    async def get_baseline_by_user_id(self, user_id: str) -> Optional[ClientBaseline]:
        """Get the most recent baseline for a user"""
        try:
            logger.info(f"=== BaselineRepository.get_baseline_by_user_id called ===")
            logger.info(f"user_id: {user_id}")
            
            cursor = self.collection.find({"user_id": user_id}).sort("created_at", -1).limit(1)
            result = await cursor.to_list(length=1)
            
            if result:
                # Convert ObjectId to string for Pydantic model
                if "_id" in result[0]:
                    result[0]["_id"] = str(result[0]["_id"])
                baseline = ClientBaseline(**result[0])
                logger.info(f"✅ Found baseline for user: {user_id}")
                return baseline
            else:
                logger.info(f"No baseline found for user: {user_id}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error getting baseline by user ID: {e}")
            return None
    
    async def update_baseline(self, baseline_id: str, update_data: Dict[str, Any]) -> Optional[ClientBaseline]:
        """Update a baseline"""
        try:
            logger.info(f"=== BaselineRepository.update_baseline called ===")
            logger.info(f"baseline_id: {baseline_id}")
            
            if not ObjectId.is_valid(baseline_id):
                logger.error(f"Invalid ObjectId: {baseline_id}")
                return None
            
            update_data["updated_at"] = datetime.utcnow()
            
            result = await self.collection.find_one_and_update(
                {"_id": ObjectId(baseline_id)},
                {"$set": update_data},
                return_document=True
            )
            
            if result:
                logger.info(f"✅ Updated baseline: {baseline_id}")
                # Convert ObjectId to string for Pydantic model
                if "_id" in result:
                    result["_id"] = str(result["_id"])
                return ClientBaseline(**result)
            else:
                logger.error(f"Baseline not found for update: {baseline_id}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error updating baseline: {e}")
            return None