"""
Journey System API Endpoints

This module contains FastAPI routes for the Journey System functionality.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
import logging

from app.api.v1.deps import org_optional
from app.schemas.journey import (
    ReflectionCreateRequest, ReflectionResponse, ReflectionWithInsightsResponse,
    InsightCreateRequest, InsightResponse, JourneyFeedResponse, JourneyFeedItem
)
from app.services.journey.journey_service import JourneyService
from app.repositories.journey.reflection_repository import ReflectionRepository
from app.repositories.journey.insight_repository import InsightRepository

logger = logging.getLogger(__name__)

router = APIRouter()


def get_journey_service() -> JourneyService:
    """Dependency to get JourneyService instance"""
    reflection_repo = ReflectionRepository()
    insight_repo = InsightRepository()
    return JourneyService(reflection_repo, insight_repo)




@router.get("/feed", response_model=JourneyFeedResponse)
async def get_journey_feed(
    skip: int = Query(0, ge=0, description="Number of items to skip for pagination"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of items to return"),
    user_info: dict = Depends(org_optional),
    journey_service: JourneyService = Depends(get_journey_service)
):
    """
    Get the user's journey feed containing reflections and insights in chronological order.
    
    This endpoint returns a paginated feed of the user's journey items (reflections and insights)
    sorted by creation date in descending order (most recent first).
    """
    try:
        user_id = user_info['clerk_user_id']
        logger.info(f"Getting journey feed for user: {user_id} (skip={skip}, limit={limit})")
        
        # Get the feed items from the service
        feed_items_data = await journey_service.get_user_journey_feed(user_id, skip, limit)
        
        # Convert to response format
        feed_items = []
        for item_data in feed_items_data:
            feed_item = JourneyFeedItem(
                type=item_data["type"],
                id=item_data["id"],
                title=item_data["title"],
                content=item_data.get("content"),
                summary=item_data.get("summary"),
                description=item_data.get("description"),
                categories=item_data.get("categories"),
                category=item_data.get("category"),
                tags=item_data.get("tags", []),
                processing_status=item_data.get("processing_status"),
                review_status=item_data.get("review_status"),
                insight_count=item_data.get("insight_count"),
                source_id=item_data.get("source_id"),
                source_title=item_data.get("source_title"),
                is_favorite=item_data.get("is_favorite"),
                is_actionable=item_data.get("is_actionable"),
                suggested_actions=item_data.get("suggested_actions"),
                confidence_score=item_data.get("confidence_score"),
                user_rating=item_data.get("user_rating"),
                view_count=item_data.get("view_count"),
                created_at=item_data["created_at"],
                updated_at=item_data["updated_at"],
                generated_at=item_data.get("generated_at")
            )
            feed_items.append(feed_item)
        
        return JourneyFeedResponse(
            items=feed_items,
            total_count=len(feed_items),
            skip=skip,
            limit=limit
        )
        
    except Exception as e:
        logger.error(f"❌ Error getting journey feed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get journey feed: {str(e)}"
        )


@router.post("/reflections", response_model=ReflectionResponse, status_code=status.HTTP_201_CREATED)
async def create_reflection(
    reflection_data: ReflectionCreateRequest,
    user_info: dict = Depends(org_optional),
    journey_service: JourneyService = Depends(get_journey_service)
):
    """
    Create a new reflection source.
    
    This endpoint creates a new reflection that can be processed to generate insights.
    The reflection will be automatically processed if auto_process is True.
    """
    try:
        user_id = user_info['clerk_user_id']
        logger.info(f"Creating reflection for user: {user_id}")
        
        # Convert request to dict
        reflection_dict = reflection_data.dict()
        
        # Create the reflection
        created_reflection = await journey_service.create_reflection(user_id, reflection_dict)
        
        # Convert to response format
        return ReflectionResponse(
            id=str(created_reflection.id),
            title=created_reflection.title,
            description=created_reflection.description,
            content=created_reflection.content,
            categories=created_reflection.categories,
            tags=created_reflection.tags,
            processing_status=created_reflection.processing_status,
            insight_count=len(created_reflection.insight_ids),
            word_count=created_reflection.word_count,
            created_at=created_reflection.created_at,
            updated_at=created_reflection.updated_at
        )
        
    except Exception as e:
        logger.error(f"❌ Error creating reflection: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create reflection: {str(e)}"
        )


@router.get("/reflections/{reflection_id}", response_model=ReflectionWithInsightsResponse)
async def get_reflection_with_insights(
    reflection_id: str,
    user_info: dict = Depends(org_optional),
    journey_service: JourneyService = Depends(get_journey_service)
):
    """
    Get a specific reflection with its associated insights.
    
    This endpoint returns a reflection and all insights that have been generated from it.
    """
    try:
        user_id = user_info['clerk_user_id']
        logger.info(f"Getting reflection with insights: {reflection_id} for user: {user_id}")
        
        # Get reflection with insights
        result = await journey_service.get_reflection_with_insights(reflection_id)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reflection not found"
            )
        
        reflection_data = result["reflection"]
        insights_data = result["insights"]
        
        # Verify ownership
        if reflection_data["user_id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Not your reflection"
            )
        
        # Convert reflection to response format
        reflection_response = ReflectionResponse(
            id=reflection_data["id"],
            title=reflection_data["title"],
            description=reflection_data.get("description"),
            content=reflection_data.get("content"),
            categories=reflection_data.get("categories", []),
            tags=reflection_data.get("tags", []),
            processing_status=reflection_data["processing_status"],
            insight_count=len(insights_data),
            word_count=reflection_data.get("word_count"),
            created_at=reflection_data["created_at"],
            updated_at=reflection_data["updated_at"]
        )
        
        # Convert insights to response format
        insights_response = []
        for insight_data in insights_data:
            insight_response = InsightResponse(
                id=insight_data["id"],
                title=insight_data["title"],
                content=insight_data["content"],
                summary=insight_data.get("summary"),
                category=insight_data["category"],
                subcategories=insight_data.get("subcategories", []),
                tags=insight_data.get("tags", []),
                source_id=insight_data["source_id"],
                source_title=insight_data.get("source_title"),
                source_excerpt=insight_data.get("source_excerpt"),
                review_status=insight_data["review_status"],
                confidence_score=insight_data.get("confidence_score"),
                is_favorite=insight_data.get("is_favorite", False),
                is_actionable=insight_data.get("is_actionable", False),
                suggested_actions=insight_data.get("suggested_actions", []),
                user_rating=insight_data.get("user_rating"),
                view_count=insight_data.get("view_count", 0),
                created_at=insight_data["created_at"],
                updated_at=insight_data["updated_at"],
                generated_at=insight_data["generated_at"]
            )
            insights_response.append(insight_response)
        
        return ReflectionWithInsightsResponse(
            reflection=reflection_response,
            insights=insights_response,
            insight_count=len(insights_response)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting reflection with insights: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get reflection: {str(e)}"
        )


@router.post("/reflections/{reflection_id}/insights", response_model=InsightResponse, status_code=status.HTTP_201_CREATED)
async def add_insight_to_reflection(
    reflection_id: str,
    insight_data: InsightCreateRequest,
    user_info: dict = Depends(org_optional),
    journey_service: JourneyService = Depends(get_journey_service)
):
    """
    Add a new insight to a reflection.
    
    This endpoint creates a new insight and links it to the specified reflection.
    The reflection must belong to the authenticated user.
    """
    try:
        user_id = user_info['clerk_user_id']
        logger.info(f"Adding insight to reflection: {reflection_id} for user: {user_id}")
        
        # Convert request to dict
        insight_dict = insight_data.dict()
        
        # Create the insight and link to reflection
        created_insight = await journey_service.add_insight_to_reflection(reflection_id, insight_dict)
        
        # Verify ownership (the service should handle this, but double-check)
        if created_insight.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Not your reflection"
            )
        
        # Convert to response format
        return InsightResponse(
            id=str(created_insight.id),
            title=created_insight.title,
            content=created_insight.content,
            summary=created_insight.summary,
            category=created_insight.category,
            subcategories=created_insight.subcategories,
            tags=created_insight.tags,
            source_id=created_insight.source_id,
            source_title=created_insight.source_title,
            source_excerpt=created_insight.source_excerpt,
            review_status=created_insight.review_status,
            confidence_score=created_insight.confidence_score,
            is_favorite=created_insight.is_favorite,
            is_actionable=created_insight.is_actionable,
            suggested_actions=created_insight.suggested_actions,
            user_rating=created_insight.user_rating,
            view_count=created_insight.view_count,
            created_at=created_insight.created_at,
            updated_at=created_insight.updated_at,
            generated_at=created_insight.generated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error adding insight to reflection: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add insight: {str(e)}"
        )

