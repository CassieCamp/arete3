from fastapi import APIRouter, Depends, HTTPException, status
from app.api.v1.deps import get_current_user_clerk_id
from app.services.profile_service import ProfileService
from app.schemas.profile import ProfileResponse, ProfileCreateRequest, ProfileUpdateRequest
from app.core.config import settings
from typing import Dict, Any

router = APIRouter()


@router.get("/me")
async def get_current_user(
    clerk_user_id: str = Depends(get_current_user_clerk_id)
):
    """Get current user's basic information"""
    from app.services.user_service import UserService
    
    user_service = UserService()
    user = await user_service.get_user_by_clerk_id(clerk_user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "id": str(user.id),
        "clerk_user_id": user.clerk_user_id,
        "email": user.email,
        "role": user.role,
        "onboarding_state": user.onboarding_state,
        "created_at": user.created_at.isoformat()
    }


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


@router.get("/access/check-coach-authorization")
async def check_coach_authorization(
    clerk_user_id: str = Depends(get_current_user_clerk_id)
):
    """Check if current user is authorized to be a coach"""
    from app.services.user_service import UserService
    import logging
    
    logger = logging.getLogger(__name__)
    
    user_service = UserService()
    user = await user_service.get_user_by_clerk_id(clerk_user_id)
    
    logger.info(f"Checking authorization for clerk_user_id: {clerk_user_id}")
    logger.info(f"User found: {user is not None}")
    if user:
        logger.info(f"User email: {user.email}")
        logger.info(f"Whitelist emails: {settings.coach_whitelist_emails_list}")
        logger.info(f"Email in whitelist: {user.email.lower() in settings.coach_whitelist_emails_list}")
    
    if not user or not user.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User email not found for clerk_user_id: {clerk_user_id}"
        )
    
    is_authorized = user.email.lower() in settings.coach_whitelist_emails_list
    
    return {
        "authorized": is_authorized,
        "email": user.email,
        "message": "Authorized to create coach profile" if is_authorized else "Not authorized for coach access"
    }


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
    coach_user = await user_service.get_user_by_email(coach_email)
    
    if not coach_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coach not found in system. They may need to complete their registration first."
        )
    
    # Check if coach has a profile
    profile_service = ProfileService()
    coach_profile = await profile_service.get_profile_by_clerk_id(coach_user.clerk_user_id)
    
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


@router.post("/dev/create-current-user")
async def create_current_user_manually(
    clerk_user_id: str = Depends(get_current_user_clerk_id)
):
    """Development endpoint to manually create current user in database"""
    from app.services.user_service import UserService
    import clerk
    
    user_service = UserService()
    
    # Check if user already exists
    existing_user = await user_service.get_user_by_clerk_id(clerk_user_id)
    if existing_user:
        return {
            "success": True,
            "message": "User already exists",
            "user_id": str(existing_user.id),
            "email": existing_user.email,
            "clerk_user_id": existing_user.clerk_user_id
        }
    
    # Get user email from Clerk
    try:
        clerk_client = clerk.Client(api_key=settings.clerk_secret_key)
        clerk_user = clerk_client.users.get(clerk_user_id)
        
        # Get primary email
        primary_email = None
        if clerk_user.email_addresses:
            for email in clerk_user.email_addresses:
                if email.id == clerk_user.primary_email_address_id:
                    primary_email = email.email_address
                    break
            
            # Fallback to first email if primary not found
            if not primary_email:
                primary_email = clerk_user.email_addresses[0].email_address
        
        if not primary_email:
            return {
                "success": False,
                "message": "No email found for user in Clerk"
            }
        
        # Create user in our database
        user = await user_service.create_user_from_clerk(
            clerk_user_id=clerk_user_id,
            email=primary_email,
            role="client"  # Default role
        )
        
        return {
            "success": True,
            "message": "User created successfully",
            "user_id": str(user.id),
            "email": user.email,
            "clerk_user_id": user.clerk_user_id
        }
        
    except Exception as e:
        logger.error(f"Error fetching user from Clerk: {e}")
        return {
            "success": False,
            "message": f"Error creating user: {str(e)}"
        }


@router.get("/me/onboarding")
async def get_onboarding_state(
    clerk_user_id: str = Depends(get_current_user_clerk_id)
):
    """Get current user's onboarding state"""
    from app.services.user_service import UserService
    
    user_service = UserService()
    onboarding_state = await user_service.get_onboarding_state(clerk_user_id)
    
    if onboarding_state is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"onboarding_state": onboarding_state}


@router.post("/me/onboarding/start")
async def start_onboarding(
    clerk_user_id: str = Depends(get_current_user_clerk_id)
):
    """Start onboarding process for current user"""
    from app.services.user_service import UserService
    
    user_service = UserService()
    updated_user = await user_service.start_onboarding(clerk_user_id)
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "success": True,
        "message": "Onboarding started",
        "onboarding_state": updated_user.onboarding_state
    }


@router.post("/me/onboarding/step/{step}")
async def complete_onboarding_step(
    step: int,
    clerk_user_id: str = Depends(get_current_user_clerk_id)
):
    """Complete a specific onboarding step"""
    from app.services.user_service import UserService
    
    if step < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Step must be a non-negative integer"
        )
    
    user_service = UserService()
    updated_user = await user_service.complete_onboarding_step(clerk_user_id, step)
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "success": True,
        "message": f"Step {step} completed",
        "onboarding_state": updated_user.onboarding_state
    }


@router.post("/me/onboarding/complete")
async def complete_onboarding(
    clerk_user_id: str = Depends(get_current_user_clerk_id)
):
    """Mark onboarding as completed"""
    from app.services.user_service import UserService
    
    user_service = UserService()
    updated_user = await user_service.complete_onboarding(clerk_user_id)
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "success": True,
        "message": "Onboarding completed",
        "onboarding_state": updated_user.onboarding_state
    }


@router.put("/me/onboarding")
async def update_onboarding_state(
    request: Dict[str, Any],
    clerk_user_id: str = Depends(get_current_user_clerk_id)
):
    """Update user's onboarding state"""
    from app.services.user_service import UserService
    
    onboarding_state = request.get("onboarding_state")
    if not onboarding_state:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="onboarding_state is required"
        )
    
    user_service = UserService()
    updated_user = await user_service.update_onboarding_state(clerk_user_id, onboarding_state)
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "success": True,
        "message": "Onboarding state updated",
        "onboarding_state": updated_user.onboarding_state
    }