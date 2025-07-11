from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
from app.services.freemium_service import FreemiumService
from app.api.v1.deps import get_current_user
from app.models.user import User
from pydantic import BaseModel
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class FreemiumStatusResponse(BaseModel):
    has_coach: bool
    entries_count: int
    max_free_entries: int
    coach_requested: bool
    coach_request_date: Optional[datetime] = None
    can_create_entries: bool
    can_access_insights: bool
    can_access_destinations: bool
    is_freemium: bool
    entries_remaining: Optional[int] = None

class CoachRequestData(BaseModel):
    context: str
    context_message: str
    goals: str
    experience_level: str
    preferred_coaching_style: str
    availability: str
    specific_challenges: Optional[str] = None
    motivation: Optional[str] = None
    user_info: dict

@router.get("/status", response_model=FreemiumStatusResponse)
async def get_freemium_status(current_user: User = Depends(get_current_user)):
    """Get freemium status for the current user"""
    try:
        logger.info(f"Getting freemium status for user: {current_user.clerk_user_id}")
        
        freemium_service = FreemiumService()
        status = await freemium_service.get_freemium_status(current_user.clerk_user_id)
        
        return FreemiumStatusResponse(**status)
        
    except Exception as e:
        logger.error(f"Error getting freemium status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve freemium status"
        )

@router.post("/request-coach")
async def request_coach(
    request_data: CoachRequestData,
    current_user: User = Depends(get_current_user)
):
    """Submit a request for coach access"""
    try:
        logger.info(f"Processing coach request for user: {current_user.clerk_user_id}")
        
        freemium_service = FreemiumService()
        
        # Check if user already has a coach
        current_status = await freemium_service.get_freemium_status(current_user.clerk_user_id)
        if current_status.get("has_coach", False):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already has a coach"
            )
        
        if current_status.get("coach_requested", False):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Coach request already submitted"
            )
        
        # Submit the coach request
        success = await freemium_service.request_coach(current_user.clerk_user_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to submit coach request"
            )
        
        # Store the detailed request data (this could be expanded to save to a separate collection)
        logger.info(f"Coach request details for {current_user.clerk_user_id}: {request_data.model_dump()}")
        
        return {
            "message": "Coach request submitted successfully",
            "status": "pending_review"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing coach request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process coach request"
        )

@router.post("/check-entry-limit")
async def check_entry_limit(current_user: User = Depends(get_current_user)):
    """Check if user can create a new entry"""
    try:
        logger.info(f"Checking entry limit for user: {current_user.clerk_user_id}")
        
        freemium_service = FreemiumService()
        can_create = await freemium_service.can_create_entry(current_user.clerk_user_id)
        
        return {
            "can_create_entry": can_create,
            "user_id": current_user.clerk_user_id
        }
        
    except Exception as e:
        logger.error(f"Error checking entry limit: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check entry limit"
        )

@router.post("/increment-entry-count")
async def increment_entry_count(current_user: User = Depends(get_current_user)):
    """Increment entry count for freemium users"""
    try:
        logger.info(f"Incrementing entry count for user: {current_user.clerk_user_id}")
        
        freemium_service = FreemiumService()
        success = await freemium_service.increment_entry_count(current_user.clerk_user_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to increment entry count"
            )
        
        return {
            "message": "Entry count incremented successfully",
            "user_id": current_user.clerk_user_id
        }
        
    except Exception as e:
        logger.error(f"Error incrementing entry count: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to increment entry count"
        )