from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.schemas.coaching_relationship import (
    ConnectionRequestCreate,
    ConnectionRequestResponse,
    CoachingRelationshipResponse,
    UserRelationshipsResponse
)
from app.services.coaching_relationship_service import CoachingRelationshipService
from app.repositories.coaching_relationship_repository import CoachingRelationshipRepository
from app.repositories.user_repository import UserRepository
from app.api.v1.deps import org_required
from app.models.coaching_relationship import RelationshipStatus
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


def get_coaching_relationship_service() -> CoachingRelationshipService:
    """Dependency to get coaching relationship service"""
    coaching_relationship_repository = CoachingRelationshipRepository()
    user_repository = UserRepository()
    return CoachingRelationshipService(coaching_relationship_repository, user_repository)


async def convert_relationship_to_response(relationship, user_repository: UserRepository) -> CoachingRelationshipResponse:
    """Convert CoachingRelationship model to response schema with user emails"""
    # Fetch coach and client emails
    coach_user = await user_repository.get_user_by_clerk_id(relationship.coach_user_id)
    client_user = await user_repository.get_user_by_clerk_id(relationship.client_user_id)
    
    return CoachingRelationshipResponse(
        id=str(relationship.id),
        coach_user_id=relationship.coach_user_id,
        client_user_id=relationship.client_user_id,
        coach_email=coach_user.email if coach_user else None,
        client_email=client_user.email if client_user else None,
        status=relationship.status,
        created_at=relationship.created_at,
        updated_at=relationship.updated_at
    )


@router.post("/", response_model=CoachingRelationshipResponse)
async def create_connection_request(
    request: ConnectionRequestCreate,
    user_info: dict = Depends(org_required),
    service: CoachingRelationshipService = Depends(get_coaching_relationship_service)
):
    """
    Create a new connection request (coach-initiated only)
    """
    current_user_id = user_info['clerk_user_id']
    logger.info(f"Creating connection request from coach {current_user_id} to client {request.client_email}")
    
    try:
        relationship = await service.create_connection_request(
            coach_user_id=current_user_id,
            client_email=request.client_email
        )
        
        user_repository = UserRepository()
        return await convert_relationship_to_response(relationship, user_repository)
        
    except ValueError as e:
        logger.error(f"ValueError in create_connection_request: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error in create_connection_request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while creating the connection request"
        )


@router.post("/{relationship_id}/respond", response_model=CoachingRelationshipResponse)
async def respond_to_connection_request(
    relationship_id: str,
    response: ConnectionRequestResponse,
    user_info: dict = Depends(org_required),
    service: CoachingRelationshipService = Depends(get_coaching_relationship_service)
):
    """
    Respond to a connection request (client can accept or decline coach's invitation)
    """
    current_user_id = user_info['clerk_user_id']
    logger.info(f"Client {current_user_id} responding to relationship {relationship_id} with status {response.status}")
    
    try:
        relationship = await service.respond_to_connection_request(
            relationship_id=relationship_id,
            responding_user_id=current_user_id,
            new_status=response.status
        )
        
        user_repository = UserRepository()
        return await convert_relationship_to_response(relationship, user_repository)
        
    except ValueError as e:
        logger.error(f"ValueError in respond_to_connection_request: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error in respond_to_connection_request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while responding to the connection request"
        )


@router.get("/", response_model=UserRelationshipsResponse)
async def get_user_relationships(
    user_info: dict = Depends(org_required),
    service: CoachingRelationshipService = Depends(get_coaching_relationship_service)
):
    """
    Get all connection requests and relationships for the current user
    """
    current_user_id = user_info['clerk_user_id']
    logger.info(f"Getting relationships for user {current_user_id}")
    
    try:
        relationships_data = await service.get_user_relationships(current_user_id)
        user_repository = UserRepository()
        
        # Convert relationships to response format with user emails
        pending_responses = []
        for rel in relationships_data["pending"]:
            response = await convert_relationship_to_response(rel, user_repository)
            pending_responses.append(response)
            
        active_responses = []
        for rel in relationships_data["active"]:
            response = await convert_relationship_to_response(rel, user_repository)
            active_responses.append(response)
        
        return UserRelationshipsResponse(
            pending=pending_responses,
            active=active_responses
        )
        
    except Exception as e:
        logger.error(f"Unexpected error in get_user_relationships: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving relationships"
        )