from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from app.models.coach_resource import CoachResource, CoachClientNote
from app.repositories.coach_resource_repository import CoachResourceRepository
from app.repositories.coaching_relationship_repository import CoachingRelationshipRepository
from app.services.user_service import UserService
from app.repositories.profile_repository import ProfileRepository
from app.repositories.entry_repository import EntryRepository
from app.api.v1.deps import org_required
from pydantic import BaseModel
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic models for request/response
class CoachResourceCreate(BaseModel):
    title: str
    description: Optional[str] = None
    resource_url: str
    resource_type: str  # "document" | "article" | "video" | "tool"
    is_template: bool = False
    client_specific: bool = False
    target_client_id: Optional[str] = None
    category: str  # "exercise" | "assessment" | "reading" | "framework"
    tags: List[str] = []

class CoachResourceUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    resource_url: Optional[str] = None
    resource_type: Optional[str] = None
    is_template: Optional[bool] = None
    client_specific: Optional[bool] = None
    target_client_id: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None

class ClientNotesUpdate(BaseModel):
    note_of_moment: Optional[str] = None
    way_of_working: Optional[str] = None
    about_me: Optional[str] = None

class CoachClient(BaseModel):
    id: str
    name: str
    email: str
    relationship_status: str
    entries_count: int
    last_entry_date: Optional[datetime] = None
    created_at: datetime

class CoachDashboardResponse(BaseModel):
    clients: List[CoachClient]
    total_clients: int
    active_clients: int
    pending_clients: int

@router.get("/clients", response_model=CoachDashboardResponse)
async def get_coach_clients(user_info: dict = Depends(org_required)):
    """Get coach's client list with stats"""
    try:
        clerk_user_id = user_info['clerk_user_id']
        logger.info(f"Getting clients for coach: {clerk_user_id}")
        
        # Get coaching relationships
        coaching_repo = CoachingRelationshipRepository()
        relationships = await coaching_repo.get_relationships_for_coach(clerk_user_id)
        
        # Get user and profile repositories
        user_service = UserService()
        profile_repo = ProfileRepository()
        entry_repo = EntryRepository()
        
        clients = []
        for relationship in relationships:
            # Get client user data
            client_user = user_service.get_user(relationship.client_user_id)
            if not client_user:
                continue
                
            def get_primary_email(user):
                if not user or not user.email_addresses:
                    return None
                for email in user.email_addresses:
                    if email.id == user.primary_email_address_id:
                        return email.email_address
                return user.email_addresses[0].email_address
            
            client_email = get_primary_email(client_user)

            # Get client profile for name
            client_profile = await profile_repo.get_profile_by_clerk_id(relationship.client_user_id)
            client_name = f"{client_profile.first_name} {client_profile.last_name}" if client_profile else client_email
            
            # Get client entry stats
            entries_count = await entry_repo.get_entries_count_by_user(relationship.client_user_id)
            last_entry = await entry_repo.get_latest_entry_by_user(relationship.client_user_id)
            
            clients.append(CoachClient(
                id=relationship.client_user_id,
                name=client_name,
                email=client_email,
                relationship_status=relationship.status.value,
                entries_count=entries_count,
                last_entry_date=last_entry.created_at if last_entry else None,
                created_at=relationship.created_at
            ))
        
        # Calculate stats
        total_clients = len(clients)
        active_clients = len([c for c in clients if c.relationship_status == 'active'])
        pending_clients = len([c for c in clients if c.relationship_status in ['pending', 'pending_by_coach']])
        
        return CoachDashboardResponse(
            clients=clients,
            total_clients=total_clients,
            active_clients=active_clients,
            pending_clients=pending_clients
        )
        
    except Exception as e:
        logger.error(f"Error getting coach clients: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve client data"
        )

@router.get("/resources")
async def get_coach_resources(
    category: Optional[str] = None,
    resource_type: Optional[str] = None,
    is_template: Optional[bool] = None,
    user_info: dict = Depends(org_required)
):
    """Get coach's resources with optional filters"""
    try:
        clerk_user_id = user_info['clerk_user_id']
        logger.info(f"Getting resources for coach: {clerk_user_id}")
        
        coach_resource_repo = CoachResourceRepository()
        resources = await coach_resource_repo.get_resources_by_coach(
            clerk_user_id,
            category=category,
            resource_type=resource_type,
            is_template=is_template
        )
        
        return {"resources": resources}
        
    except Exception as e:
        logger.error(f"Error getting coach resources: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve resources"
        )

@router.post("/resources")
async def create_coach_resource(
    resource_data: CoachResourceCreate,
    user_info: dict = Depends(org_required)
):
    """Create a new coach resource"""
    try:
        clerk_user_id = user_info['clerk_user_id']
        logger.info(f"Creating resource for coach: {clerk_user_id}")
        
        # Create resource model
        resource = CoachResource(
            coach_user_id=clerk_user_id,
            **resource_data.model_dump()
        )
        
        coach_resource_repo = CoachResourceRepository()
        created_resource = await coach_resource_repo.create_resource(resource)
        
        return {"resource": created_resource}
        
    except Exception as e:
        logger.error(f"Error creating coach resource: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create resource"
        )

@router.put("/resources/{resource_id}")
async def update_coach_resource(
    resource_id: str,
    resource_data: CoachResourceUpdate,
    user_info: dict = Depends(org_required)
):
    """Update a coach resource"""
    try:
        clerk_user_id = user_info['clerk_user_id']
        logger.info(f"Updating resource {resource_id} for coach: {clerk_user_id}")
        
        coach_resource_repo = CoachResourceRepository()
        
        # Verify resource belongs to coach
        existing_resource = await coach_resource_repo.get_resource_by_id(resource_id)
        if not existing_resource or existing_resource.coach_user_id != clerk_user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resource not found"
            )
        
        # Update resource
        update_data = {k: v for k, v in resource_data.model_dump().items() if v is not None}
        updated_resource = await coach_resource_repo.update_resource(resource_id, update_data)
        
        if not updated_resource:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update resource"
            )
        
        return {"resource": updated_resource}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating coach resource: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update resource"
        )

@router.delete("/resources/{resource_id}")
async def delete_coach_resource(
    resource_id: str,
    user_info: dict = Depends(org_required)
):
    """Delete a coach resource"""
    try:
        clerk_user_id = user_info['clerk_user_id']
        logger.info(f"Deleting resource {resource_id} for coach: {clerk_user_id}")
        
        coach_resource_repo = CoachResourceRepository()
        
        # Verify resource belongs to coach
        existing_resource = await coach_resource_repo.get_resource_by_id(resource_id)
        if not existing_resource or existing_resource.coach_user_id != clerk_user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resource not found"
            )
        
        # Delete resource (soft delete)
        success = await coach_resource_repo.delete_resource(resource_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete resource"
            )
        
        return {"message": "Resource deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting coach resource: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete resource"
        )

@router.get("/clients/{client_id}/notes")
async def get_client_notes(
    client_id: str,
    user_info: dict = Depends(org_required)
):
    """Get coach's notes for specific client"""
    try:
        clerk_user_id = user_info['clerk_user_id']
        logger.info(f"Getting notes for client {client_id} by coach: {clerk_user_id}")
        
        # Verify coaching relationship exists
        coaching_repo = CoachingRelationshipRepository()
        relationship = await coaching_repo.get_relationship_between_users(
            clerk_user_id, client_id
        )
        if not relationship:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Coaching relationship not found"
            )
        
        coach_resource_repo = CoachResourceRepository()
        notes = await coach_resource_repo.get_client_note(clerk_user_id, client_id)
        
        return {"notes": notes}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting client notes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve client notes"
        )

@router.put("/clients/{client_id}/notes")
async def update_client_notes(
    client_id: str,
    notes_data: ClientNotesUpdate,
    user_info: dict = Depends(org_required)
):
    """Update coach's notes for specific client"""
    try:
        clerk_user_id = user_info['clerk_user_id']
        logger.info(f"Updating notes for client {client_id} by coach: {clerk_user_id}")
        
        # Verify coaching relationship exists
        coaching_repo = CoachingRelationshipRepository()
        relationship = await coaching_repo.get_relationship_between_users(
            clerk_user_id, client_id
        )
        if not relationship:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Coaching relationship not found"
            )
        
        coach_resource_repo = CoachResourceRepository()
        
        # Check if notes exist, create or update accordingly
        existing_notes = await coach_resource_repo.get_client_note(clerk_user_id, client_id)
        
        if existing_notes:
            # Update existing notes
            update_data = {k: v for k, v in notes_data.model_dump().items() if v is not None}
            updated_notes = await coach_resource_repo.update_client_note(
                clerk_user_id, client_id, update_data
            )
        else:
            # Create new notes
            new_notes = CoachClientNote(
                coach_user_id=clerk_user_id,
                client_user_id=client_id,
                **notes_data.model_dump()
            )
            updated_notes = await coach_resource_repo.create_client_note(new_notes)
        
        return {"notes": updated_notes}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating client notes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update client notes"
        )

@router.get("/clients/{client_id}/insights")
async def get_client_insights(
    client_id: str,
    user_info: dict = Depends(org_required)
):
    """Get client insights for coach view (read-only)"""
    try:
        clerk_user_id = user_info['clerk_user_id']
        logger.info(f"Getting insights for client {client_id} by coach: {clerk_user_id}")
        
        # Verify coaching relationship exists
        coaching_repo = CoachingRelationshipRepository()
        relationship = await coaching_repo.get_relationship_between_users(
            clerk_user_id, client_id
        )
        if not relationship or relationship.status != 'active':
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Active coaching relationship not found"
            )
        
        # Get client entries and insights
        entry_repo = EntryRepository()
        entries = await entry_repo.get_entries_by_user(client_id, limit=10)
        
        # Get client destinations - REMOVED: destination functionality deprecated
        
        return {
            "client_id": client_id,
            "recent_entries": entries,
            "entries_count": await entry_repo.get_entries_count_by_user(client_id)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting client insights: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve client insights"
        )

@router.get("/clients/{client_id}/resources")
async def get_client_resources(
    client_id: str,
    user_info: dict = Depends(org_required)
):
    """Get resources assigned to a specific client"""
    try:
        clerk_user_id = user_info['clerk_user_id']
        logger.info(f"Getting resources for client {client_id} by coach: {clerk_user_id}")
        
        # Verify coaching relationship exists
        coaching_repo = CoachingRelationshipRepository()
        relationship = await coaching_repo.get_relationship_between_users(
            clerk_user_id, client_id
        )
        if not relationship:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Coaching relationship not found"
            )
        
        coach_resource_repo = CoachResourceRepository()
        resources = await coach_resource_repo.get_client_specific_resources(
            clerk_user_id, client_id
        )
        
        return {"resources": resources}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting client resources: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve client resources"
        )