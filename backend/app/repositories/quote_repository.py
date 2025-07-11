from typing import List, Optional, Dict, Any
from app.models.quote import Quote, UserQuoteLike
from app.db.mongodb import get_database
from bson import ObjectId
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class QuoteRepository:
    def __init__(self):
        self.quotes_collection_name = "quotes"
        self.likes_collection_name = "user_quote_likes"

    async def create_quote(self, quote: Quote) -> Quote:
        """Create a new quote"""
        try:
            db = get_database()
            quote_dict = quote.model_dump(by_alias=True, exclude={"id"})
            
            # Remove the id field if it's None or empty
            if "_id" in quote_dict and quote_dict["_id"] is None:
                del quote_dict["_id"]
            
            result = await db[self.quotes_collection_name].insert_one(quote_dict)
            
            # Fetch the created quote
            created_quote = await db[self.quotes_collection_name].find_one({"_id": result.inserted_id})
            
            # Convert ObjectId to string for Pydantic model
            if created_quote and "_id" in created_quote:
                created_quote["_id"] = str(created_quote["_id"])
            
            return Quote(**created_quote)
            
        except Exception as e:
            logger.error(f"Error creating quote: {e}")
            raise

    async def get_quote_by_id(self, quote_id: str) -> Optional[Quote]:
        """Get quote by ID"""
        try:
            if not ObjectId.is_valid(quote_id):
                return None
                
            db = get_database()
            quote_data = await db[self.quotes_collection_name].find_one({"_id": ObjectId(quote_id)})
            
            if quote_data:
                # Convert ObjectId to string for Pydantic model
                quote_data["_id"] = str(quote_data["_id"])
                return Quote(**quote_data)
            return None
            
        except Exception as e:
            logger.error(f"Error fetching quote {quote_id}: {e}")
            return None

    async def get_quotes_by_category(self, category: str, limit: int = 10) -> List[Quote]:
        """Get quotes by category"""
        try:
            db = get_database()
            cursor = db[self.quotes_collection_name].find(
                {"category": category, "active": True}
            ).sort("created_at", -1).limit(limit)
            
            quotes = []
            async for quote_data in cursor:
                # Convert ObjectId to string for Pydantic model
                if "_id" in quote_data:
                    quote_data["_id"] = str(quote_data["_id"])
                quotes.append(Quote(**quote_data))
            
            return quotes
            
        except Exception as e:
            logger.error(f"Error fetching quotes for category {category}: {e}")
            return []

    async def get_random_quotes(self, count: int = 5, exclude_user_likes: Optional[str] = None) -> List[Quote]:
        """Get random quotes, optionally excluding user's liked quotes"""
        try:
            db = get_database()
            
            # Build aggregation pipeline
            pipeline = [
                {"$match": {"active": True}},
                {"$sample": {"size": count * 2}}  # Get more than needed to filter out likes
            ]
            
            # If excluding user likes, get their liked quote IDs first
            excluded_quote_ids = []
            if exclude_user_likes:
                user_likes = await self.get_user_liked_quotes(exclude_user_likes)
                excluded_quote_ids = [like.quote_id for like in user_likes]
            
            cursor = db[self.quotes_collection_name].aggregate(pipeline)
            quotes = []
            
            async for quote_data in cursor:
                # Convert ObjectId to string for Pydantic model
                if "_id" in quote_data:
                    quote_id = str(quote_data["_id"])
                    quote_data["_id"] = quote_id
                    
                    # Skip if user has already liked this quote
                    if quote_id not in excluded_quote_ids:
                        quotes.append(Quote(**quote_data))
                        
                        # Stop when we have enough quotes
                        if len(quotes) >= count:
                            break
            
            return quotes
            
        except Exception as e:
            logger.error(f"Error fetching random quotes: {e}")
            return []

    async def update_quote(self, quote_id: str, update_data: Dict[str, Any]) -> Optional[Quote]:
        """Update quote"""
        try:
            if not ObjectId.is_valid(quote_id):
                return None
            
            db = get_database()
            update_data["updated_at"] = datetime.utcnow()
            
            result = await db[self.quotes_collection_name].update_one(
                {"_id": ObjectId(quote_id)},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                return await self.get_quote_by_id(quote_id)
            return None
            
        except Exception as e:
            logger.error(f"Error updating quote {quote_id}: {e}")
            return None

    async def increment_display_count(self, quote_id: str) -> bool:
        """Increment the display count for a quote"""
        try:
            if not ObjectId.is_valid(quote_id):
                return False
            
            db = get_database()
            result = await db[self.quotes_collection_name].update_one(
                {"_id": ObjectId(quote_id)},
                {"$inc": {"display_count": 1}}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error incrementing display count for quote {quote_id}: {e}")
            return False

    # User Quote Likes methods
    async def like_quote(self, user_id: str, quote_id: str) -> bool:
        """Like a quote (toggle like status)"""
        try:
            db = get_database()
            
            # Check if already liked
            existing_like = await db[self.likes_collection_name].find_one({
                "user_id": user_id,
                "quote_id": quote_id
            })
            
            if existing_like:
                # Unlike - remove the like
                await db[self.likes_collection_name].delete_one({
                    "user_id": user_id,
                    "quote_id": quote_id
                })
                
                # Decrement like count
                await db[self.quotes_collection_name].update_one(
                    {"_id": ObjectId(quote_id)},
                    {"$inc": {"like_count": -1}}
                )
                return False  # Unliked
            else:
                # Like - add the like
                like = UserQuoteLike(user_id=user_id, quote_id=quote_id)
                like_dict = like.model_dump(by_alias=True, exclude={"id"})
                
                if "_id" in like_dict and like_dict["_id"] is None:
                    del like_dict["_id"]
                
                await db[self.likes_collection_name].insert_one(like_dict)
                
                # Increment like count
                await db[self.quotes_collection_name].update_one(
                    {"_id": ObjectId(quote_id)},
                    {"$inc": {"like_count": 1}}
                )
                return True  # Liked
            
        except Exception as e:
            logger.error(f"Error toggling like for quote {quote_id} by user {user_id}: {e}")
            return False

    async def get_user_liked_quotes(self, user_id: str) -> List[UserQuoteLike]:
        """Get all quotes liked by a user"""
        try:
            db = get_database()
            cursor = db[self.likes_collection_name].find({"user_id": user_id})
            
            likes = []
            async for like_data in cursor:
                # Convert ObjectId to string for Pydantic model
                if "_id" in like_data:
                    like_data["_id"] = str(like_data["_id"])
                likes.append(UserQuoteLike(**like_data))
            
            return likes
            
        except Exception as e:
            logger.error(f"Error fetching liked quotes for user {user_id}: {e}")
            return []

    async def get_user_favorite_quotes(self, user_id: str, limit: int = 10) -> List[Quote]:
        """Get quotes that a user has liked"""
        try:
            db = get_database()
            
            # Get user's liked quote IDs
            user_likes = await self.get_user_liked_quotes(user_id)
            liked_quote_ids = [ObjectId(like.quote_id) for like in user_likes]
            
            if not liked_quote_ids:
                return []
            
            # Get the actual quotes
            cursor = db[self.quotes_collection_name].find(
                {"_id": {"$in": liked_quote_ids}, "active": True}
            ).limit(limit)
            
            quotes = []
            async for quote_data in cursor:
                # Convert ObjectId to string for Pydantic model
                if "_id" in quote_data:
                    quote_data["_id"] = str(quote_data["_id"])
                quotes.append(Quote(**quote_data))
            
            return quotes
            
        except Exception as e:
            logger.error(f"Error fetching favorite quotes for user {user_id}: {e}")
            return []

    async def is_quote_liked_by_user(self, user_id: str, quote_id: str) -> bool:
        """Check if a quote is liked by a user"""
        try:
            db = get_database()
            like = await db[self.likes_collection_name].find_one({
                "user_id": user_id,
                "quote_id": quote_id
            })
            return like is not None
            
        except Exception as e:
            logger.error(f"Error checking if quote {quote_id} is liked by user {user_id}: {e}")
            return False