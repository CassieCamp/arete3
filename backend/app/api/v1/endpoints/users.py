from fastapi import APIRouter, Depends, HTTPException, status
from app.api.v1.deps import get_current_user_clerk_id
from app.services.profile_service import ProfileService
from app.schemas.profile import ProfileResponse, ProfileCreateRequest, ProfileUpdateRequest
from typing import Dict, Any

router = APIRouter()


@router.get("/me/profile", response_model=ProfileResponse)
async def get_user_profile(
    clerk_user_id: str = Depends(get_current_user_clerk_id)
):
    """Get current user's profile"""
    profile_service = ProfileService()
    
    profile = await profile_service.get_profile_by_clerk_id(clerk_user_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    return ProfileResponse(
        id=str(profile.id),
        user_id=profile.user_id,
        first_name=profile.first_name,
        last_name=profile.last_name,
        coach_data=profile.coach_data,
        client_data=profile.client_data,
        created_at=profile.created_at.isoformat(),
        updated_at=profile.updated_at.isoformat()
    )


@router.put("/me/profile", response_model=ProfileResponse)
async def update_user_profile(
    profile_data: ProfileUpdateRequest,
    clerk_user_id: str = Depends(get_current_user_clerk_id)
):
    """Update current user's profile"""
    profile_service = ProfileService()
    
    # Convert to dict, excluding None values
    update_data = profile_data.dict(exclude_unset=True)
    
    updated_profile = await profile_service.update_profile(clerk_user_id, update_data)
    if not updated_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    return ProfileResponse(
        id=str(updated_profile.id),
        user_id=updated_profile.user_id,
        first_name=updated_profile.first_name,
        last_name=updated_profile.last_name,
        coach_data=updated_profile.coach_data,
        client_data=updated_profile.client_data,
        created_at=updated_profile.created_at.isoformat(),
        updated_at=updated_profile.updated_at.isoformat()
    )


@router.post("/me/profile", response_model=ProfileResponse)
async def create_user_profile(
    profile_data: ProfileCreateRequest,
    clerk_user_id: str = Depends(get_current_user_clerk_id)
):
    """Create current user's profile"""
    profile_service = ProfileService()
    
    # Check if profile already exists
    existing_profile = await profile_service.get_profile_by_clerk_id(clerk_user_id)
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Profile already exists"
        )
    
    # Convert to dict
    create_data = profile_data.dict()
    
    created_profile = await profile_service.create_profile(clerk_user_id, create_data)
    
    return ProfileResponse(
        id=str(created_profile.id),
        user_id=created_profile.user_id,
        first_name=created_profile.first_name,
        last_name=created_profile.last_name,
        coach_data=created_profile.coach_data,
        client_data=created_profile.client_data,
        created_at=created_profile.created_at.isoformat(),
        updated_at=created_profile.updated_at.isoformat()
    )