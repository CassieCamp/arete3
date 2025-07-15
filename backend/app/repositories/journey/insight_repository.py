from typing import Optional, List, Dict, Any
from bson import ObjectId
from app.db.mongodb import get_database
from app.models.journey.insight import Insight
from app.models.journey.enums import CategoryType

class InsightRepository:
    """Repository for managing insights in MongoDB."""

    def __init__(self):
        self.collection_name = Insight.Config.collection_name

    async def create(self, insight: Insight) -> Insight:
        """Create a new insight."""
        db = get_database()
        insight_dict = insight.model_dump(by_alias=True, exclude_unset=True)
        if "_id" in insight_dict and insight_dict["_id"] is None:
            del insight_dict["_id"]

        result = await db[self.collection_name].insert_one(insight_dict)
        insight.id = str(result.inserted_id)
        return insight

    async def get_by_id(self, insight_id: str) -> Optional[Insight]:
        """Get an insight by its ID."""
        db = get_database()
        doc = await db[self.collection_name].find_one({"_id": ObjectId(insight_id)})
        if doc:
            doc["_id"] = str(doc["_id"])
            return Insight(**doc)
        return None

    async def get_all_for_user(self, user_id: str, skip: int = 0, limit: int = 100) -> List[Insight]:
        """Get all insights for a user."""
        db = get_database()
        cursor = db[self.collection_name].find({"user_id": user_id}).skip(skip).limit(limit).sort("created_at", -1)
        docs = await cursor.to_list(length=limit)
        return [Insight(**doc) for doc in docs]

    async def get_by_categories(self, user_id: str, categories: List[CategoryType], skip: int = 0, limit: int = 100) -> List[Insight]:
        """Get insights by a list of categories for a user."""
        db = get_database()
        query = {
            "user_id": user_id,
            "category": {"$in": categories}
        }
        cursor = db[self.collection_name].find(query).skip(skip).limit(limit).sort("created_at", -1)
        docs = await cursor.to_list(length=limit)
        return [Insight(**doc) for doc in docs]