from fastapi import APIRouter, Depends, HTTPException, status
from app.api.v1.deps import org_optional
from app.services.profile_service import ProfileService
from app.schemas.profile import ProfileResponse, ProfileCreateRequest, ProfileUpdateRequest
from app.core.config import settings
from typing import Dict, Any

router = APIRouter()


@router.get("/me")
async def get_current_user(
    user_info: dict = Depends(org_optional)
):
    """Get current user's basic information from Clerk"""
    from app.services.user_service import UserService
    
    clerk_user_id = user_info['clerk_user_id']
    user_service = UserService()
    user = user_service.get_user(clerk_user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in Clerk"
        )
    
    def get_primary_email(user):
        if not user or not user.email_addresses:
            return None
        for email in user.email_addresses:
            if email.id == user.primary_email_address_id:
                return email.email_address
        return user.email_addresses[0].email_address

    return {
        "clerk_user_id": user.id,
        "email": get_primary_email(user),
        "primary_role": user.public_metadata.get("primary_role", "member"),
        "organization_roles": user.public_metadata.get("organization_roles", {}),
        "first_name": user.first_name,
        "last_name": user.last_name,
        "image_url": user.image_url,
        "created_at": datetime.fromtimestamp(user.created_at / 1000).isoformat()
    }


@router.get("/me/profile", response_model=ProfileResponse)
async def get_user_profile(
    user_info: dict = Depends(org_optional)
):
    """Get current user's profile"""
    clerk_user_id = user_info['clerk_user_id']
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
    user_info: dict = Depends(org_optional)
):
    """Update current user's profile"""
    clerk_user_id = user_info['clerk_user_id']
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
    user_info: dict = Depends(org_optional)
):
    """Create current user's profile"""
    clerk_user_id = user_info['clerk_user_id']
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


@router.get("/access/check-coach-authorization")
async def check_coach_authorization(
    user_info: dict = Depends(org_optional)
):
    """Check if current user is authorized to be a coach"""
    from app.services.user_service import UserService
    import logging
    
    logger = logging.getLogger(__name__)
    
    clerk_user_id = user_info['clerk_user_id']
    user_service = UserService()
    user = user_service.get_user(clerk_user_id)
    
    logger.info(f"Checking authorization for clerk_user_id: {clerk_user_id}")
    logger.info(f"User found: {user is not None}")

    def get_primary_email(user):
        if not user or not user.email_addresses:
            return None
        for email in user.email_addresses:
            if email.id == user.primary_email_address_id:
                return email.email_address
        return user.email_addresses[0].email_address

    user_email = get_primary_email(user)

    if user:
        logger.info(f"User email: {user_email}")
        logger.info(f"Whitelist emails: {settings.coach_whitelist_emails_list}")
        logger.info(f"Email in whitelist: {user_email.lower() in settings.coach_whitelist_emails_list}")
    
    if not user or not user_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User email not found for clerk_user_id: {clerk_user_id}"
        )
    
    is_authorized = user_email.lower() in settings.coach_whitelist_emails_list
    
    return {
        "authorized": is_authorized,
        "email": user_email,
        "message": "Authorized to create coach profile" if is_authorized else "Not authorized for coach access"
    }

@router.get("/all")
async def get_all_users():
    """Get all users from Clerk"""
    from app.services.user_service import UserService
    
    user_service = UserService()
    users = user_service.get_all_users()
    
    if not users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No users found in Clerk"
        )
    
    return users


@router.post("/access/verify-coach-for-client")
async def verify_coach_for_client(
    request: Dict[str, Any]
):
    """Verify that a coach exists and is authorized (for client signup)"""
    from app.services.user_service import UserService
    
    # Extract coach_email from request body
    coach_email = request.get("coach_email")
    if not coach_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="coach_email is required"
        )
    
    # Check if coach email is in whitelist
    if coach_email.lower() not in settings.coach_whitelist_emails_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coach not found or not authorized"
        )
    
    # Check if coach actually exists in our system
    user_service = UserService()
    coach_user = user_service.get_user_by_email(coach_email)
    
    if not coach_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coach not found in system. They may need to complete their registration first."
        )
    
    # Check if coach has a profile
    profile_service = ProfileService()
    coach_profile = await profile_service.get_profile_by_clerk_id(coach_user.id)
    
    if not coach_profile or not coach_profile.coach_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Coach has not completed their profile setup"
        )
    
    return {
        "valid": True,
        "coach_email": coach_email,
        "coach_name": f"{coach_profile.first_name} {coach_profile.last_name}",
        "message": "Coach verified successfully"
    }



