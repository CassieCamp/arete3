from fastapi import APIRouter, Depends, HTTPException, status
from app.api.v1.deps import org_optional
from app.services.profile_service import ProfileService
from app.services.clerk_organization_service import ClerkOrganizationService
from app.schemas.profile import (
    CoachProfileCreateRequest, 
    ClientProfileCreateRequest,
    ProfileResponse,
    OrganizationResponse
)
from app.models.profile import Profile, CoachData, ClientData
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/coach", response_model=ProfileResponse)
async def create_coach_profile(
    profile_data: CoachProfileCreateRequest,
    user_info: dict = Depends(org_optional)
):
    """Create coach profile and automatically set up their Clerk organization"""
    try:
        clerk_user_id = user_info['clerk_user_id']
        profile_service = ProfileService()
        org_service = ClerkOrganizationService()
        
        # Check if profile already exists
        existing_profile = await profile_service.get_profile_by_clerk_id(clerk_user_id)
        if existing_profile:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Profile already exists"
            )
        
        # Create organization in Clerk first
        org_data = profile_data.organization.dict()
        org_data["specialties"] = profile_data.coach_data.specialties
        
        clerk_org = await org_service.create_coach_organization(clerk_user_id, org_data)
        
        # Create profile data dictionary for coach
        profile_dict = {
            "first_name": profile_data.first_name,
            "last_name": profile_data.last_name,
            "coach_data": profile_data.coach_data.dict(),
            "primary_organization_id": clerk_org["id"]
        }
        
        created_profile = await profile_service.create_profile(clerk_user_id, profile_dict)
        
        # Get organization details for response
        org_response = OrganizationResponse(
            clerk_org_id=clerk_org["id"],
            name=clerk_org["name"],
            role=clerk_org["membership_role"],
            metadata=clerk_org["metadata"]
        )
        
        return ProfileResponse(
            id=str(created_profile.id),
            user_id=created_profile.user_id,
            clerk_user_id=created_profile.clerk_user_id,
            first_name=created_profile.first_name,
            last_name=created_profile.last_name,
            coach_data=created_profile.coach_data,
            client_data=created_profile.client_data,
            primary_organization_id=created_profile.primary_organization_id,
            organization=org_response,
            created_at=created_profile.created_at.isoformat(),
            updated_at=created_profile.updated_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating coach profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create coach profile: {str(e)}"
        )


@router.post("/client", response_model=ProfileResponse)
async def create_client_profile(
    profile_data: ClientProfileCreateRequest,
    user_info: dict = Depends(org_optional)
):
    """Create client profile and set up their Clerk organization"""
    try:
        clerk_user_id = user_info['clerk_user_id']
        profile_service = ProfileService()
        org_service = ClerkOrganizationService()
        
        # Check if profile already exists
        existing_profile = await profile_service.get_profile_by_clerk_id(clerk_user_id)
        if existing_profile:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Profile already exists"
            )
        
        # Create organization in Clerk first
        org_data = profile_data.organization.dict()
        
        clerk_org = await org_service.create_client_organization(clerk_user_id, org_data)
        
        # Create profile with organization reference
        profile = Profile(
            user_id="",  # Will be set by profile service
            clerk_user_id=clerk_user_id,
            first_name=profile_data.first_name,
            last_name=profile_data.last_name,
            client_data=ClientData(**profile_data.client_data.dict()),
            primary_organization_id=clerk_org["id"]
        )
        
        created_profile = await profile_service.create_profile(clerk_user_id, profile.dict(exclude={"id", "user_id"}))
        
        # Get organization details for response
        org_response = OrganizationResponse(
            clerk_org_id=clerk_org["id"],
            name=clerk_org["name"],
            role=clerk_org["membership_role"],
            metadata=clerk_org["metadata"]
        )
        
        return ProfileResponse(
            id=str(created_profile.id),
            user_id=created_profile.user_id,
            clerk_user_id=created_profile.clerk_user_id,
            first_name=created_profile.first_name,
            last_name=created_profile.last_name,
            coach_data=created_profile.coach_data,
            client_data=created_profile.client_data,
            primary_organization_id=created_profile.primary_organization_id,
            organization=org_response,
            created_at=created_profile.created_at.isoformat(),
            updated_at=created_profile.updated_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating client profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create client profile: {str(e)}"
        )


@router.get("/me", response_model=ProfileResponse)
async def get_current_user_profile(
    user_info: dict = Depends(org_optional)
):
    """Get current user's profile with organization details"""
    try:
        clerk_user_id = user_info['clerk_user_id']
        profile_service = ProfileService()
        org_service = ClerkOrganizationService()
        
        profile = await profile_service.get_profile_by_clerk_id(clerk_user_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        
        # Get organization details if profile has one
        org_response = None
        if profile.primary_organization_id:
            try:
                org_details = await org_service.get_organization_with_metadata(profile.primary_organization_id)
                if org_details:
                    org_response = OrganizationResponse(
                        clerk_org_id=org_details["id"],
                        name=org_details["name"],
                        role="admin",  # Default role for profile owner
                        metadata=org_details["metadata"]
                    )
            except Exception as e:
                logger.warning(f"Could not fetch organization details: {str(e)}")
        
        return ProfileResponse(
            id=str(profile.id),
            user_id=profile.user_id,
            clerk_user_id=profile.clerk_user_id,
            first_name=profile.first_name,
            last_name=profile.last_name,
            coach_data=profile.coach_data,
            client_data=profile.client_data,
            primary_organization_id=profile.primary_organization_id,
            organization=org_response,
            created_at=profile.created_at.isoformat(),
            updated_at=profile.updated_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get profile: {str(e)}"
        )