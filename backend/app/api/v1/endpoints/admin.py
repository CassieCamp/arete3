from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
from app.api.v1.deps import get_current_user_clerk_id
from app.repositories.coaching_interest_repository import CoachingInterestRepository
from app.models.coaching_interest import CoachingInterest
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


async def require_admin_role(
    user_info: Dict[str, Any] = Depends(get_current_user_clerk_id)
) -> Dict[str, Any]:
    """
    Dependency that ensures the user has admin role.
    
    This dependency:
    1. Ensures the user is authenticated
    2. Checks that primary_role is 'admin'
    
    Returns user info if admin role is verified.
    """
    try:
        clerk_user_id = user_info["clerk_user_id"]
        primary_role = user_info["primary_role"]
        
        logger.info(f"🔒 require_admin_role: Checking admin access for user {clerk_user_id}")
        logger.info(f"🔒 Primary role: {primary_role}")
        
        # Check if user has admin role
        if primary_role != "admin":
            logger.warning(f"🔒 Access denied: User {clerk_user_id} has role '{primary_role}', requires 'admin'")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Admin role required"
            )
        
        logger.info(f"✅ require_admin_role: Admin access granted for user {clerk_user_id}")
        return user_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error in require_admin_role: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to validate admin access"
        )


@router.get("/coaching-interest/", response_model=List[CoachingInterest])
async def get_all_coaching_interest_submissions(
    user_info: Dict[str, Any] = Depends(require_admin_role)
) -> List[CoachingInterest]:
    """
    Get all coaching interest submissions (admin only).
    
    This endpoint allows users with the 'admin' role to retrieve all coaching
    interest submissions from the database.
    """
    try:
        logger.info(f"=== get_all_coaching_interest_submissions called ===")
        logger.info(f"Admin user: {user_info['clerk_user_id']}")
        
        # Initialize repository and get all submissions
        coaching_interest_repo = CoachingInterestRepository()
        submissions = await coaching_interest_repo.get_all()
        
        logger.info(f"✅ Successfully retrieved {len(submissions)} coaching interest submissions for admin")
        return submissions
        
    except Exception as e:
        logger.error(f"❌ Error retrieving coaching interest submissions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve coaching interest submissions"
        )