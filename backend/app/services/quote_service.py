from typing import List, Optional, Dict, Any
from app.models.quote import Quote, UserQuoteLike
from app.repositories.quote_repository import QuoteRepository
import logging

logger = logging.getLogger(__name__)


class QuoteService:
    def __init__(self):
        self.quote_repository = QuoteRepository()

    async def get_daily_quotes(self, user_id: str, count: int = 5) -> List[Dict[str, Any]]:
        """
        Return personalized quotes for daily inspiration.
        Prioritizes user's favorites and excludes recently liked quotes.
        """
        try:
            logger.info(f"=== QuoteService.get_daily_quotes called ===")
            logger.info(f"Getting {count} daily quotes for user_id: {user_id}")
            
            # Get user's favorite quotes first
            favorite_quotes = await self.quote_repository.get_user_favorite_quotes(user_id, limit=2)
            
            # Get random quotes excluding user's likes
            random_quotes = await self.quote_repository.get_random_quotes(
                count=count - len(favorite_quotes),
                exclude_user_likes=user_id
            )
            
            # Combine and format quotes
            all_quotes = favorite_quotes + random_quotes
            
            # Format quotes with like status
            formatted_quotes = []
            for quote in all_quotes[:count]:
                is_liked = await self.quote_repository.is_quote_liked_by_user(user_id, str(quote.id))
                
                formatted_quotes.append({
                    "id": str(quote.id),
                    "quote_text": quote.quote_text,
                    "author": quote.author,
                    "source": quote.source,
                    "category": quote.category,
                    "tags": quote.tags,
                    "like_count": quote.like_count,
                    "is_liked": is_liked
                })
                
                # Increment display count
                await self.quote_repository.increment_display_count(str(quote.id))
            
            logger.info(f"✅ Successfully retrieved {len(formatted_quotes)} daily quotes")
            return formatted_quotes
            
        except Exception as e:
            logger.error(f"❌ Error getting daily quotes: {e}")
            raise

    async def like_quote(self, user_id: str, quote_id: str) -> Dict[str, Any]:
        """
        Toggle like status for a quote.
        Returns the new like status and updated like count.
        """
        try:
            logger.info(f"=== QuoteService.like_quote called ===")
            logger.info(f"Toggling like for quote_id: {quote_id}, user_id: {user_id}")
            
            # Toggle like status
            is_liked = await self.quote_repository.like_quote(user_id, quote_id)
            
            # Get updated quote to return new like count
            quote = await self.quote_repository.get_quote_by_id(quote_id)
            if not quote:
                raise ValueError("Quote not found")
            
            result = {
                "quote_id": quote_id,
                "is_liked": is_liked,
                "like_count": quote.like_count,
                "action": "liked" if is_liked else "unliked"
            }
            
            logger.info(f"✅ Successfully {result['action']} quote")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error toggling quote like: {e}")
            raise

    async def get_user_favorites(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get all quotes that a user has liked.
        """
        try:
            logger.info(f"=== QuoteService.get_user_favorites called ===")
            logger.info(f"Getting favorite quotes for user_id: {user_id}")
            
            favorite_quotes = await self.quote_repository.get_user_favorite_quotes(user_id, limit)
            
            # Format quotes
            formatted_quotes = []
            for quote in favorite_quotes:
                formatted_quotes.append({
                    "id": str(quote.id),
                    "quote_text": quote.quote_text,
                    "author": quote.author,
                    "source": quote.source,
                    "category": quote.category,
                    "tags": quote.tags,
                    "like_count": quote.like_count,
                    "is_liked": True  # All these are favorites
                })
            
            logger.info(f"✅ Successfully retrieved {len(formatted_quotes)} favorite quotes")
            return formatted_quotes
            
        except Exception as e:
            logger.error(f"❌ Error getting user favorites: {e}")
            raise

    async def get_quotes_by_category(self, category: str, user_id: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get quotes by category, optionally including user's like status.
        """
        try:
            logger.info(f"=== QuoteService.get_quotes_by_category called ===")
            logger.info(f"Getting quotes for category: {category}")
            
            quotes = await self.quote_repository.get_quotes_by_category(category, limit)
            
            # Format quotes with like status if user provided
            formatted_quotes = []
            for quote in quotes:
                is_liked = False
                if user_id:
                    is_liked = await self.quote_repository.is_quote_liked_by_user(user_id, str(quote.id))
                
                formatted_quotes.append({
                    "id": str(quote.id),
                    "quote_text": quote.quote_text,
                    "author": quote.author,
                    "source": quote.source,
                    "category": quote.category,
                    "tags": quote.tags,
                    "like_count": quote.like_count,
                    "is_liked": is_liked
                })
            
            logger.info(f"✅ Successfully retrieved {len(formatted_quotes)} quotes for category {category}")
            return formatted_quotes
            
        except Exception as e:
            logger.error(f"❌ Error getting quotes by category: {e}")
            raise

    async def create_quote(self, quote_data: Dict[str, Any], created_by: str) -> Quote:
        """
        Create a new quote (admin function).
        """
        try:
            logger.info(f"=== QuoteService.create_quote called ===")
            logger.info(f"Creating quote by user: {created_by}")
            
            quote = Quote(
                quote_text=quote_data["quote_text"],
                author=quote_data["author"],
                source=quote_data.get("source"),
                category=quote_data["category"],
                tags=quote_data.get("tags", []),
                created_by=created_by
            )
            
            created_quote = await self.quote_repository.create_quote(quote)
            logger.info(f"✅ Successfully created quote with ID: {created_quote.id}")
            
            return created_quote
            
        except Exception as e:
            logger.error(f"❌ Error creating quote: {e}")
            raise

    async def update_quote(self, quote_id: str, update_data: Dict[str, Any]) -> Optional[Quote]:
        """
        Update an existing quote (admin function).
        """
        try:
            logger.info(f"=== QuoteService.update_quote called ===")
            logger.info(f"Updating quote_id: {quote_id}")
            
            # Validate allowed fields
            allowed_fields = {
                "quote_text", "author", "source", "category", "tags", "active"
            }
            
            validated_update_data = {}
            for key, value in update_data.items():
                if key in allowed_fields:
                    validated_update_data[key] = value
                else:
                    logger.warning(f"Ignoring invalid update field: {key}")
            
            if not validated_update_data:
                logger.info("No valid fields to update")
                return await self.quote_repository.get_quote_by_id(quote_id)
            
            updated_quote = await self.quote_repository.update_quote(quote_id, validated_update_data)
            
            if updated_quote:
                logger.info(f"✅ Successfully updated quote {quote_id}")
            else:
                logger.warning(f"Quote {quote_id} was not updated")
            
            return updated_quote
            
        except Exception as e:
            logger.error(f"❌ Error updating quote: {e}")
            raise

    async def get_quote_stats(self) -> Dict[str, Any]:
        """
        Get overall quote statistics (admin function).
        """
        try:
            logger.info(f"=== QuoteService.get_quote_stats called ===")
            
            # This would require additional repository methods
            # For now, return placeholder stats
            stats = {
                "total_quotes": 0,
                "total_likes": 0,
                "categories": {},
                "most_liked_quotes": []
            }
            
            logger.info(f"✅ Successfully retrieved quote stats")
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error getting quote stats: {e}")
            raise

    async def search_quotes(self, query: str, user_id: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search quotes by text content, author, or tags.
        """
        try:
            logger.info(f"=== QuoteService.search_quotes called ===")
            logger.info(f"Searching quotes with query: {query}")
            
            # This would require a search method in the repository
            # For now, return empty results
            formatted_quotes = []
            
            logger.info(f"✅ Successfully searched quotes, found {len(formatted_quotes)} results")
            return formatted_quotes
            
        except Exception as e:
            logger.error(f"❌ Error searching quotes: {e}")
            raise