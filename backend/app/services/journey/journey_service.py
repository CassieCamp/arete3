"""
Journey System Service

This module contains the core business logic for managing reflections and insights.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

from app.models.journey.reflection import ReflectionSource
from app.models.journey.insight import Insight
from app.models.journey.enums import CategoryType, ReviewStatus
from app.repositories.journey.reflection_repository import ReflectionRepository
from app.repositories.journey.insight_repository import InsightRepository

logger = logging.getLogger(__name__)


class JourneyService:
    """Service class containing core business logic for the Journey System"""
    
    def __init__(self, reflection_repository: ReflectionRepository, insight_repository: InsightRepository):
        """Initialize the service with repository instances"""
        self.reflection_repo = reflection_repository
        self.insight_repo = insight_repository
    
    async def create_reflection(self, user_id: str, reflection_data: dict) -> ReflectionSource:
        """
        Create a new reflection source
        
        Args:
            user_id: Clerk user ID of the owner
            reflection_data: Dictionary containing reflection data
            
        Returns:
            ReflectionSource: The created reflection
        """
        logger.info(f"Creating reflection for user: {user_id}")
        
        try:
            # Ensure user_id is set
            reflection_data["user_id"] = user_id
            
            # Set default timestamps if not provided
            if "created_at" not in reflection_data:
                reflection_data["created_at"] = datetime.utcnow()
            if "updated_at" not in reflection_data:
                reflection_data["updated_at"] = datetime.utcnow()
            
            # Create reflection instance
            reflection = ReflectionSource(**reflection_data)
            
            # Save to database
            created_reflection = await self.reflection_repo.create(reflection)
            
            logger.info(f"✅ Successfully created reflection: {created_reflection.id}")
            return created_reflection
            
        except Exception as e:
            logger.error(f"❌ Error creating reflection: {e}")
            raise
    
    async def get_reflection_with_insights(self, reflection_id: str) -> dict:
        """
        Retrieve a reflection and its associated insights
        
        Args:
            reflection_id: ID of the reflection to retrieve
            
        Returns:
            dict: Dictionary containing reflection and its insights
        """
        logger.info(f"Getting reflection with insights: {reflection_id}")
        
        try:
            # Get the reflection
            reflection = await self.reflection_repo.get_by_id(reflection_id)
            if not reflection:
                logger.warning(f"Reflection not found: {reflection_id}")
                return None
            
            # Get associated insights
            insights = await self.insight_repo.get_by_reflection_id(reflection_id)
            
            # Compile result
            result = {
                "reflection": reflection.model_dump(),
                "insights": [insight.model_dump() for insight in insights],
                "insight_count": len(insights)
            }
            
            logger.info(f"✅ Retrieved reflection with {len(insights)} insights")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error getting reflection with insights: {e}")
            raise
    
    async def get_user_journey_feed(self, user_id: str, skip: int = 0, limit: int = 50) -> List[dict]:
        """
        Compile a chronological feed of a user's reflections and insights
        
        Args:
            user_id: Clerk user ID
            skip: Number of items to skip for pagination
            limit: Maximum number of items to return
            
        Returns:
            List[dict]: Chronological feed of journey items
        """
        logger.info(f"Getting journey feed for user: {user_id} (skip={skip}, limit={limit})")
        
        try:
            # Get user's reflections and insights
            reflections = await self.reflection_repo.get_all_for_user(user_id, skip=0, limit=limit*2)
            insights = await self.insight_repo.get_all_for_user(user_id, skip=0, limit=limit*2)
            
            # Create feed items with type and timestamp
            feed_items = []
            
            # Add reflections to feed
            for reflection in reflections:
                feed_items.append({
                    "type": "reflection",
                    "id": str(reflection.id),
                    "title": reflection.title,
                    "content": reflection.content,
                    "description": reflection.description,
                    "categories": reflection.categories,
                    "tags": reflection.tags,
                    "processing_status": reflection.processing_status,
                    "insight_count": len(reflection.insight_ids),
                    "created_at": reflection.created_at,
                    "updated_at": reflection.updated_at
                })
            
            # Add insights to feed
            for insight in insights:
                feed_items.append({
                    "type": "insight",
                    "id": str(insight.id),
                    "title": insight.title,
                    "content": insight.content,
                    "summary": insight.summary,
                    "category": insight.category,
                    "subcategories": insight.subcategories,
                    "tags": insight.tags,
                    "source_id": insight.source_id,
                    "source_title": insight.source_title,
                    "review_status": insight.review_status,
                    "is_favorite": insight.is_favorite,
                    "is_actionable": insight.is_actionable,
                    "suggested_actions": insight.suggested_actions,
                    "confidence_score": insight.confidence_score,
                    "user_rating": insight.user_rating,
                    "view_count": insight.view_count,
                    "created_at": insight.created_at,
                    "updated_at": insight.updated_at,
                    "generated_at": insight.generated_at
                })
            
            # Sort by creation date (most recent first)
            feed_items.sort(key=lambda x: x["created_at"], reverse=True)
            
            # Apply pagination
            paginated_feed = feed_items[skip:skip + limit]
            
            logger.info(f"✅ Generated journey feed with {len(paginated_feed)} items")
            return paginated_feed
            
        except Exception as e:
            logger.error(f"❌ Error getting user journey feed: {e}")
            raise
    
    async def add_insight_to_reflection(self, reflection_id: str, insight_data: dict) -> Insight:
        """
        Create a new insight and link it to a reflection
        
        Args:
            reflection_id: ID of the reflection to link to
            insight_data: Dictionary containing insight data
            
        Returns:
            Insight: The created insight
        """
        logger.info(f"Adding insight to reflection: {reflection_id}")
        
        try:
            # Get the reflection to ensure it exists and get user_id
            reflection = await self.reflection_repo.get_by_id(reflection_id)
            if not reflection:
                raise ValueError(f"Reflection not found: {reflection_id}")
            
            # Set required fields
            insight_data["source_id"] = reflection_id
            insight_data["user_id"] = reflection.user_id
            insight_data["source_title"] = reflection.title
            
            # Set default timestamps if not provided
            if "created_at" not in insight_data:
                insight_data["created_at"] = datetime.utcnow()
            if "updated_at" not in insight_data:
                insight_data["updated_at"] = datetime.utcnow()
            if "generated_at" not in insight_data:
                insight_data["generated_at"] = datetime.utcnow()
            
            # Create insight instance
            insight = Insight(**insight_data)
            
            # Save insight to database
            created_insight = await self.insight_repo.create(insight)
            
            # Update reflection to include this insight ID
            await self.reflection_repo.add_insight_id(reflection_id, str(created_insight.id))
            
            logger.info(f"✅ Successfully created insight and linked to reflection")
            return created_insight
            
        except Exception as e:
            logger.error(f"❌ Error adding insight to reflection: {e}")
            raise
    
    async def get_user_insights_by_category(self, user_id: str, category: CategoryType, skip: int = 0, limit: int = 100) -> List[Insight]:
        """
        Get insights by category for a user
        
        Args:
            user_id: Clerk user ID
            category: Category to filter by
            skip: Number of items to skip for pagination
            limit: Maximum number of items to return
            
        Returns:
            List[Insight]: List of insights in the specified category
        """
        logger.info(f"Getting insights by category: {category} for user: {user_id}")
        
        try:
            insights = await self.insight_repo.get_by_category(user_id, category, skip, limit)
            logger.info(f"✅ Found {len(insights)} insights for category: {category}")
            return insights
            
        except Exception as e:
            logger.error(f"❌ Error getting insights by category: {e}")
            raise
    
    async def get_user_reflections_by_category(self, user_id: str, category: CategoryType, skip: int = 0, limit: int = 100) -> List[ReflectionSource]:
        """
        Get reflections by category for a user
        
        Args:
            user_id: Clerk user ID
            category: Category to filter by
            skip: Number of items to skip for pagination
            limit: Maximum number of items to return
            
        Returns:
            List[ReflectionSource]: List of reflections in the specified category
        """
        logger.info(f"Getting reflections by category: {category} for user: {user_id}")
        
        try:
            reflections = await self.reflection_repo.get_by_category(user_id, category, skip, limit)
            logger.info(f"✅ Found {len(reflections)} reflections for category: {category}")
            return reflections
            
        except Exception as e:
            logger.error(f"❌ Error getting reflections by category: {e}")
            raise
    
    async def get_user_favorite_insights(self, user_id: str, skip: int = 0, limit: int = 100) -> List[Insight]:
        """
        Get favorite insights for a user
        
        Args:
            user_id: Clerk user ID
            skip: Number of items to skip for pagination
            limit: Maximum number of items to return
            
        Returns:
            List[Insight]: List of favorite insights
        """
        logger.info(f"Getting favorite insights for user: {user_id}")
        
        try:
            insights = await self.insight_repo.get_favorites_for_user(user_id, skip, limit)
            logger.info(f"✅ Found {len(insights)} favorite insights")
            return insights
            
        except Exception as e:
            logger.error(f"❌ Error getting favorite insights: {e}")
            raise
    
    async def get_user_actionable_insights(self, user_id: str, skip: int = 0, limit: int = 100) -> List[Insight]:
        """
        Get actionable insights for a user
        
        Args:
            user_id: Clerk user ID
            skip: Number of items to skip for pagination
            limit: Maximum number of items to return
            
        Returns:
            List[Insight]: List of actionable insights
        """
        logger.info(f"Getting actionable insights for user: {user_id}")
        
        try:
            insights = await self.insight_repo.get_actionable_for_user(user_id, skip, limit)
            logger.info(f"✅ Found {len(insights)} actionable insights")
            return insights
            
        except Exception as e:
            logger.error(f"❌ Error getting actionable insights: {e}")
            raise
    
    async def search_user_insights(self, user_id: str, query: str, skip: int = 0, limit: int = 100) -> List[Insight]:
        """
        Search insights by text content for a user
        
        Args:
            user_id: Clerk user ID
            query: Search query string
            skip: Number of items to skip for pagination
            limit: Maximum number of items to return
            
        Returns:
            List[Insight]: List of insights matching the search query
        """
        logger.info(f"Searching insights for user: {user_id} with query: {query}")
        
        try:
            insights = await self.insight_repo.search_insights(user_id, query, skip, limit)
            logger.info(f"✅ Found {len(insights)} insights matching search query")
            return insights
            
        except Exception as e:
            logger.error(f"❌ Error searching insights: {e}")
            raise
    
    async def toggle_insight_favorite(self, insight_id: str) -> Optional[Insight]:
        """
        Toggle favorite status of an insight
        
        Args:
            insight_id: ID of the insight to toggle
            
        Returns:
            Optional[Insight]: Updated insight or None if not found
        """
        logger.info(f"Toggling favorite status for insight: {insight_id}")
        
        try:
            # Get current insight
            insight = await self.insight_repo.get_by_id(insight_id)
            if not insight:
                logger.warning(f"Insight not found: {insight_id}")
                return None
            
            # Toggle favorite status
            if insight.is_favorite:
                updated_insight = await self.insight_repo.remove_from_favorites(insight_id)
            else:
                updated_insight = await self.insight_repo.mark_as_favorite(insight_id)
            
            logger.info(f"✅ Toggled favorite status for insight")
            return updated_insight
            
        except Exception as e:
            logger.error(f"❌ Error toggling insight favorite: {e}")
            raise
    
    async def get_user_journey_stats(self, user_id: str) -> dict:
        """
        Get journey statistics for a user
        
        Args:
            user_id: Clerk user ID
            
        Returns:
            dict: Dictionary containing journey statistics
        """
        logger.info(f"Getting journey stats for user: {user_id}")
        
        try:
            # Get counts
            reflection_count = await self.reflection_repo.count_for_user(user_id)
            insight_count = await self.insight_repo.count_for_user(user_id)
            
            # Get favorite insights count
            favorite_insights = await self.insight_repo.get_favorites_for_user(user_id, skip=0, limit=1000)
            favorite_count = len(favorite_insights)
            
            # Get actionable insights count
            actionable_insights = await self.insight_repo.get_actionable_for_user(user_id, skip=0, limit=1000)
            actionable_count = len(actionable_insights)
            
            stats = {
                "reflection_count": reflection_count,
                "insight_count": insight_count,
                "favorite_insight_count": favorite_count,
                "actionable_insight_count": actionable_count,
                "total_journey_items": reflection_count + insight_count
            }
            
            logger.info(f"✅ Generated journey stats: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error getting journey stats: {e}")
            raise