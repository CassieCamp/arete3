from fastapi import APIRouter, Depends, HTTPException, status
from app.api.v1.deps import get_current_user_clerk_id
from app.services.clerk_invitation_service import ClerkInvitationService
from app.services.profile_service import ProfileService
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class InvitationRequest(BaseModel):
    client_email: str
    client_first_name: str
    client_last_name: str
    message: Optional[str] = ""
    client_organization_name: Optional[str] = ""


class InvitationResponse(BaseModel):
    clerk_invitation_id: str
    status: str
    client_email: str
    expires_at: Optional[str]
    invitation_url: Optional[str]
    coach_name: str
    coach_organization: str


class RelationshipResponse(BaseModel):
    client_user_id: str
    client_name: str
    client_email: Optional[str]
    relationship_status: str
    started_at: Optional[str]
    clerk_membership_id: str


class PendingInvitationResponse(BaseModel):
    clerk_invitation_id: str
    client_email: str
    client_name: str
    status: str
    expires_at: Optional[str]
    message: Optional[str]


class CoachRelationshipsResponse(BaseModel):
    active_relationships: List[RelationshipResponse]
    pending_invitations: List[PendingInvitationResponse]


class ClientRelationshipResponse(BaseModel):
    coach_organization_id: str
    coach_organization_name: str
    relationship_status: str
    joined_at: Optional[str]
    role: str
    coach_specialties: List[str]
    coach_website: Optional[str]


class ClientRelationshipsResponse(BaseModel):
    coach_relationships: List[ClientRelationshipResponse]


@router.post("/invite", response_model=InvitationResponse)
async def send_coaching_invitation(
    invitation_data: InvitationRequest,
    clerk_user_id: str = Depends(get_current_user_clerk_id)
):
    """Send a coaching invitation using Clerk's system"""
    try:
        invitation_service = ClerkInvitationService()
        
        # Verify coach has proper authorization and profile
        profile_service = ProfileService()
        coach_profile = await profile_service.get_profile_by_clerk_id(clerk_user_id)
        
        if not coach_profile or not coach_profile.coach_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Coach profile required to send invitations"
            )
        
        if not coach_profile.primary_organization_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Coach must have an organization to send invitations"
            )
        
        # Send invitation
        result = await invitation_service.send_coaching_invitation(
            clerk_user_id, 
            invitation_data.dict()
        )
        
        return InvitationResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending coaching invitation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send invitation: {str(e)}"
        )


@router.get("/coach", response_model=CoachRelationshipsResponse)
async def get_coach_relationships(
    clerk_user_id: str = Depends(get_current_user_clerk_id)
):
    """Get coach's client relationships from Clerk memberships and invitations"""
    try:
        invitation_service = ClerkInvitationService()
        
        relationships = await invitation_service.get_coach_relationships(clerk_user_id)
        
        # Format active relationships
        active_relationships = [
            RelationshipResponse(
                client_user_id=rel["client_user_id"],
                client_name=rel["client_name"],
                client_email=rel.get("client_email"),
                relationship_status=rel["relationship_status"],
                started_at=rel.get("started_at"),
                clerk_membership_id=rel["clerk_membership_id"]
            )
            for rel in relationships["active_relationships"]
        ]
        
        # Format pending invitations
        pending_invitations = [
            PendingInvitationResponse(
                clerk_invitation_id=inv["clerk_invitation_id"],
                client_email=inv["client_email"],
                client_name=inv["client_name"],
                status=inv["status"],
                expires_at=inv.get("expires_at"),
                message=inv.get("message")
            )
            for inv in relationships["pending_invitations"]
        ]
        
        return CoachRelationshipsResponse(
            active_relationships=active_relationships,
            pending_invitations=pending_invitations
        )
        
    except Exception as e:
        logger.error(f"Error getting coach relationships: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get relationships: {str(e)}"
        )


@router.get("/client", response_model=ClientRelationshipsResponse)
async def get_client_relationships(
    clerk_user_id: str = Depends(get_current_user_clerk_id)
):
    """Get client's coach relationships from Clerk memberships"""
    try:
        invitation_service = ClerkInvitationService()
        
        relationships = await invitation_service.get_client_relationships(clerk_user_id)
        
        # Format coach relationships
        coach_relationships = [
            ClientRelationshipResponse(
                coach_organization_id=rel["coach_organization_id"],
                coach_organization_name=rel["coach_organization_name"],
                relationship_status=rel["relationship_status"],
                joined_at=rel.get("joined_at"),
                role=rel["role"],
                coach_specialties=rel.get("coach_specialties", []),
                coach_website=rel.get("coach_website")
            )
            for rel in relationships["coach_relationships"]
        ]
        
        return ClientRelationshipsResponse(
            coach_relationships=coach_relationships
        )
        
    except Exception as e:
        logger.error(f"Error getting client relationships: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get relationships: {str(e)}"
        )


@router.get("/invitations/{invitation_id}")
async def get_invitation_details(invitation_id: str):
    """Get invitation details by ID (public endpoint for invitation acceptance)"""
    try:
        invitation_service = ClerkInvitationService()
        
        invitation = await invitation_service.get_invitation_details(invitation_id)
        
        if not invitation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invitation not found or expired"
            )
        
        return {
            "invitation_id": invitation["invitation_id"],
            "status": invitation["status"],
            "email_address": invitation["email_address"],
            "expires_at": invitation.get("expires_at"),
            "coach_name": invitation.get("coach_name"),
            "message": invitation.get("message"),
            "client_organization_name": invitation.get("client_organization_name"),
            "invitation_type": invitation.get("invitation_type")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting invitation details: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get invitation details: {str(e)}"
        )


@router.delete("/invitations/{invitation_id}")
async def revoke_invitation(
    invitation_id: str,
    clerk_user_id: str = Depends(get_current_user_clerk_id)
):
    """Revoke/cancel a pending invitation"""
    try:
        invitation_service = ClerkInvitationService()
        
        # TODO: Add authorization check to ensure user can revoke this invitation
        
        success = await invitation_service.revoke_invitation(invitation_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to revoke invitation"
            )
        
        return {"message": "Invitation revoked successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error revoking invitation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to revoke invitation: {str(e)}"
        )