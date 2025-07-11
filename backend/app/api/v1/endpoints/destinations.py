from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.api.v1.deps import get_current_user_clerk_id
from app.services.destination_service import DestinationService
from app.models.destination import Destination
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=dict)
async def get_destinations(
    current_user_id: str = Depends(get_current_user_clerk_id)
):
    """Get all destinations for the current user"""
    logger.info(f"=== GET /destinations called ===")
    logger.info(f"Getting destinations for user: {current_user_id}")
    
    try:
        destination_service = DestinationService()
        destinations = await destination_service.get_destinations(current_user_id)
        
        # Convert destinations to dict format for frontend
        destinations_data = []
        for dest in destinations:
            dest_dict = {
                "id": str(dest.id),
                "destination_statement": dest.destination_statement,
                "success_vision": dest.success_vision,
                "is_big_idea": dest.is_big_idea,
                "big_idea_rank": dest.big_idea_rank,
                "progress_percentage": dest.progress_percentage,
                "progress_emoji": dest.progress_emoji,
                "progress_notes": dest.progress_notes,
                "priority": dest.priority,
                "category": dest.category,
                "status": dest.status,
                "tags": dest.tags,
                "created_at": dest.created_at.isoformat(),
                "updated_at": dest.updated_at.isoformat()
            }
            destinations_data.append(dest_dict)
        
        return {
            "destinations": destinations_data,
            "total_count": len(destinations_data)
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting destinations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get destinations: {str(e)}"
        )


@router.get("/three-big-ideas", response_model=dict)
async def get_three_big_ideas(
    current_user_id: str = Depends(get_current_user_clerk_id)
):
    """Get the three big ideas for the current user"""
    logger.info(f"=== GET /destinations/three-big-ideas called ===")
    logger.info(f"Getting three big ideas for user: {current_user_id}")
    
    try:
        destination_service = DestinationService()
        big_ideas = await destination_service.get_three_big_ideas(current_user_id)
        
        # Convert big ideas to dict format for frontend
        big_ideas_data = []
        for idea in big_ideas:
            idea_dict = {
                "id": str(idea.id),
                "destination_statement": idea.destination_statement,
                "success_vision": idea.success_vision,
                "is_big_idea": idea.is_big_idea,
                "big_idea_rank": idea.big_idea_rank,
                "progress_percentage": idea.progress_percentage,
                "progress_emoji": idea.progress_emoji,
                "progress_notes": idea.progress_notes,
                "priority": idea.priority,
                "category": idea.category,
                "status": idea.status,
                "tags": idea.tags,
                "created_at": idea.created_at.isoformat(),
                "updated_at": idea.updated_at.isoformat()
            }
            big_ideas_data.append(idea_dict)
        
        return {
            "big_ideas": big_ideas_data,
            "total_count": len(big_ideas_data)
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting three big ideas: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get three big ideas: {str(e)}"
        )