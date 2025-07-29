from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.coaching_relationship import UserRelationshipsResponse
from app.schemas.coaching_interest import CoachingInterestCreate
from app.schemas.session import UserSessionSettingsUpdate
from app.services.coaching_relationship_service import CoachingRelationshipService
from app.services.user_service import UserService
from app.repositories.coaching_relationship_repository import CoachingRelationshipRepository
from app.repositories.coaching_interest_repository import CoachingInterestRepository
from app.api.v1.deps import org_optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


def get_coaching_relationship_service() -> CoachingRelationshipService:
    """Dependency to get coaching relationship service"""
    coaching_relationship_repository = CoachingRelationshipRepository()
    user_service = UserService()
    return CoachingRelationshipService(coaching_relationship_repository, user_service)


def get_user_service() -> UserService:
    """Dependency to get user service"""
    return UserService()


def convert_relationship_to_response(relationship, user_service: UserService):
    """Convert CoachingRelationship model to response schema with user emails"""
    from app.schemas.coaching_relationship import CoachingRelationshipResponse
    
    # Fetch coach and client emails
    coach_user = user_service.get_user(relationship.coach_user_id)
    client_user = user_service.get_user(relationship.client_user_id)
    
    def get_primary_email(user):
        if not user or not user.email_addresses:
            return None
        for email in user.email_addresses:
            if email.id == user.primary_email_address_id:
                return email.email_address
        return user.email_addresses[0].email_address

    return CoachingRelationshipResponse(
        id=str(relationship.id),
        coach_user_id=relationship.coach_user_id,
        client_user_id=relationship.client_user_id,
        coach_email=get_primary_email(coach_user),
        client_email=get_primary_email(client_user),
        status=relationship.status,
        created_at=relationship.created_at,
        updated_at=relationship.updated_at
    )


@router.get("/coaching-relationships", response_model=UserRelationshipsResponse)
async def get_member_coaching_relationships(
    user_info: dict = Depends(org_optional),
    service: CoachingRelationshipService = Depends(get_coaching_relationship_service)
):
    """
    Get coaching relationships for members - allows members to access their own coaching relationships
    where they are the member/client in the relationship
    """
    current_user_id = user_info['clerk_user_id']
    logger.info(f"Getting member coaching relationships for user {current_user_id}")
    
    try:
        # Get relationships where the current user is the member/client
        relationships_data = await service.get_user_relationships(current_user_id)
        user_service = UserService()
        
        # Convert relationships to response format with user emails
        pending_responses = []
        for rel in relationships_data["pending"]:
            # Only include relationships where current user is the client/member
            if rel.client_user_id == current_user_id:
                response = convert_relationship_to_response(rel, user_service)
                pending_responses.append(response)
            
        active_responses = []
        for rel in relationships_data["active"]:
            # Only include relationships where current user is the client/member
            if rel.client_user_id == current_user_id:
                response = convert_relationship_to_response(rel, user_service)
                active_responses.append(response)
        
        return UserRelationshipsResponse(
            pending=pending_responses,
            active=active_responses
        )
        
    except Exception as e:
        logger.error(f"Unexpected error in get_member_coaching_relationships: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving member coaching relationships"
        )


@router.post("/coaching-interest")
async def submit_coaching_interest(
    coaching_interest: CoachingInterestCreate
):
    """
    Submit coaching interest form - saves submission to database
    """
    logger.info(f"Coaching interest submission from {coaching_interest.name} ({coaching_interest.email})")
    
    try:
        # Initialize coaching interest repository
        coaching_interest_repository = CoachingInterestRepository()
        
        # Save submission to database
        saved_submission = await coaching_interest_repository.create(coaching_interest)
        
        logger.info(f"✅ Successfully saved coaching interest from {coaching_interest.name} with ID: {saved_submission.id}")
        return {
            "message": "Thank you for your interest in coaching! We'll be in touch soon.",
            "status": "success",
            "submission_id": str(saved_submission.id)
        }
        
    except Exception as e:
        logger.error(f"Unexpected error in submit_coaching_interest: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing your request"
        )


@router.get("/session-settings")
async def get_session_settings(
    user_info: dict = Depends(org_optional),
    user_service: UserService = Depends(get_user_service)
):
    """
    Get current user's session settings
    """
    current_user_id = user_info['clerk_user_id']
    logger.info(f"Getting session settings for user {current_user_id}")
    
    try:
        user = user_service.get_user(current_user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {
            "session_auto_send_context": user.public_metadata.get("session_auto_send_context", False)
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_session_settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving session settings"
        )


@router.put("/session-settings")
async def update_session_settings(
    settings: UserSessionSettingsUpdate,
    user_info: dict = Depends(org_optional),
    user_service: UserService = Depends(get_user_service)
):
    """
    Update current user's session settings
    """
    current_user_id = user_info['clerk_user_id']
    logger.info(f"Updating session settings for user {current_user_id}: {settings}")
    
    try:
        from clerk_backend_api import Clerk
        clerk_client = Clerk()
        updated_user = clerk_client.users.update_user(
            user_id=current_user_id,
            public_metadata={
                "session_auto_send_context": settings.session_auto_send_context
            }
        )
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        logger.info(f"✅ Successfully updated session settings for user {current_user_id}")
        return {
            "message": "Session settings updated successfully",
            "session_auto_send_context": updated_user.public_metadata.get("session_auto_send_context")
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error in update_session_settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while updating session settings"
        )