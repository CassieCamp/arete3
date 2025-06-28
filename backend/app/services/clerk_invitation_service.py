from typing import Optional, Dict, Any, List
import httpx
from app.core.config import settings
from app.services.profile_service import ProfileService
import logging

logger = logging.getLogger(__name__)


class ClerkInvitationService:
    """Service for managing Clerk invitations for coaching relationships"""
    
    def __init__(self):
        self.base_url = "https://api.clerk.com/v1"
        self.headers = {
            "Authorization": f"Bearer {settings.clerk_secret_key}",
            "Content-Type": "application/json"
        }
        self.profile_service = ProfileService()
    
    async def send_coaching_invitation(self, coach_user_id: str, invitation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send coaching invitation using Clerk's system"""
        try:
            # Get coach's profile and organization
            coach_profile = await self.profile_service.get_profile_by_clerk_id(coach_user_id)
            if not coach_profile or not coach_profile.primary_organization_id:
                raise Exception("Coach must have a profile and organization to send invitations")
            
            coach_org_id = coach_profile.primary_organization_id
            
            # Create invitation with coaching context metadata
            invitation_metadata = {
                "invitation_type": "coaching_relationship",
                "coach_user_id": coach_user_id,
                "coach_name": f"{coach_profile.first_name} {coach_profile.last_name}",
                "message": invitation_data.get("message", ""),
                "client_organization_name": invitation_data.get("client_organization_name", ""),
                "client_first_name": invitation_data.get("client_first_name", ""),
                "client_last_name": invitation_data.get("client_last_name", "")
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/invitations",
                    headers=self.headers,
                    json={
                        "organization_id": coach_org_id,
                        "email_address": invitation_data["client_email"],
                        "role": "member",
                        "private_metadata": invitation_metadata,
                        "redirect_url": f"{settings.frontend_url}/invitations/accept"
                    }
                )
                
                if response.status_code != 200:
                    logger.error(f"Failed to create invitation: {response.text}")
                    raise Exception(f"Failed to create invitation: {response.status_code}")
                
                clerk_invitation = response.json()
                
                return {
                    "clerk_invitation_id": clerk_invitation["id"],
                    "status": clerk_invitation["status"],
                    "client_email": invitation_data["client_email"],
                    "expires_at": clerk_invitation.get("expires_at"),
                    "invitation_url": clerk_invitation.get("url"),
                    "coach_name": f"{coach_profile.first_name} {coach_profile.last_name}",
                    "coach_organization": coach_org_id
                }
                
        except Exception as e:
            logger.error(f"Error sending coaching invitation: {str(e)}")
            raise
    
    async def get_invitation_details(self, invitation_id: str) -> Optional[Dict[str, Any]]:
        """Get invitation details by ID"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/invitations/{invitation_id}",
                    headers=self.headers
                )
                
                if response.status_code == 404:
                    return None
                
                if response.status_code != 200:
                    logger.error(f"Failed to get invitation: {response.text}")
                    raise Exception(f"Failed to get invitation: {response.status_code}")
                
                invitation = response.json()
                metadata = invitation.get("private_metadata", {})
                
                return {
                    "invitation_id": invitation["id"],
                    "status": invitation["status"],
                    "email_address": invitation["email_address"],
                    "expires_at": invitation.get("expires_at"),
                    "coach_name": metadata.get("coach_name"),
                    "coach_user_id": metadata.get("coach_user_id"),
                    "message": metadata.get("message"),
                    "client_organization_name": metadata.get("client_organization_name"),
                    "invitation_type": metadata.get("invitation_type")
                }
                
        except Exception as e:
            logger.error(f"Error getting invitation details: {str(e)}")
            raise
    
    async def get_coach_relationships(self, coach_user_id: str) -> Dict[str, Any]:
        """Get coach's relationships from Clerk memberships and invitations"""
        try:
            # Get coach's profile and organization
            coach_profile = await self.profile_service.get_profile_by_clerk_id(coach_user_id)
            if not coach_profile or not coach_profile.primary_organization_id:
                return {"active_relationships": [], "pending_invitations": []}
            
            coach_org_id = coach_profile.primary_organization_id
            
            async with httpx.AsyncClient() as client:
                # Get organization memberships (active relationships)
                memberships_response = await client.get(
                    f"{self.base_url}/organizations/{coach_org_id}/memberships",
                    headers=self.headers
                )
                
                # Get pending invitations
                invitations_response = await client.get(
                    f"{self.base_url}/organizations/{coach_org_id}/invitations",
                    headers=self.headers,
                    params={"status": "pending"}
                )
                
                active_relationships = []
                if memberships_response.status_code == 200:
                    memberships = memberships_response.json()
                    for membership in memberships:
                        user_data = membership.get("public_user_data", {})
                        # Skip the coach themselves
                        if user_data.get("user_id") != coach_user_id:
                            active_relationships.append({
                                "client_user_id": user_data.get("user_id"),
                                "client_name": f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip(),
                                "client_email": user_data.get("email_addresses", [{}])[0].get("email_address"),
                                "relationship_status": "active",
                                "started_at": membership.get("created_at"),
                                "clerk_membership_id": membership.get("id")
                            })
                
                pending_invitations = []
                if invitations_response.status_code == 200:
                    invitations = invitations_response.json()
                    for invitation in invitations:
                        metadata = invitation.get("private_metadata", {})
                        if metadata.get("invitation_type") == "coaching_relationship":
                            pending_invitations.append({
                                "clerk_invitation_id": invitation["id"],
                                "client_email": invitation["email_address"],
                                "client_name": f"{metadata.get('client_first_name', '')} {metadata.get('client_last_name', '')}".strip(),
                                "status": invitation["status"],
                                "expires_at": invitation.get("expires_at"),
                                "message": metadata.get("message")
                            })
                
                return {
                    "active_relationships": active_relationships,
                    "pending_invitations": pending_invitations
                }
                
        except Exception as e:
            logger.error(f"Error getting coach relationships: {str(e)}")
            raise
    
    async def get_client_relationships(self, client_user_id: str) -> Dict[str, Any]:
        """Get client's coach relationships from Clerk memberships"""
        try:
            async with httpx.AsyncClient() as client:
                # Get user's organization memberships
                response = await client.get(
                    f"{self.base_url}/users/{client_user_id}/organization_memberships",
                    headers=self.headers
                )
                
                if response.status_code != 200:
                    logger.error(f"Failed to get client memberships: {response.text}")
                    return {"coach_relationships": []}
                
                memberships = response.json()
                coach_relationships = []
                
                for membership in memberships:
                    org = membership.get("organization", {})
                    org_metadata = org.get("private_metadata", {})
                    
                    # Check if this is a coach organization
                    if org_metadata.get("organization_type") == "coach_practice":
                        coach_relationships.append({
                            "coach_organization_id": org.get("id"),
                            "coach_organization_name": org.get("name"),
                            "relationship_status": "active",
                            "joined_at": membership.get("created_at"),
                            "role": membership.get("role"),
                            "coach_specialties": org_metadata.get("specialties", []),
                            "coach_website": org_metadata.get("website")
                        })
                
                return {"coach_relationships": coach_relationships}
                
        except Exception as e:
            logger.error(f"Error getting client relationships: {str(e)}")
            raise
    
    async def revoke_invitation(self, invitation_id: str) -> bool:
        """Revoke/cancel a pending invitation"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/invitations/{invitation_id}/revoke",
                    headers=self.headers
                )
                
                return response.status_code == 200
                
        except Exception as e:
            logger.error(f"Error revoking invitation: {str(e)}")
            return False
    
    async def get_organization_invitations(self, org_id: str, status: str = "pending") -> List[Dict[str, Any]]:
        """Get all invitations for an organization"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/organizations/{org_id}/invitations",
                    headers=self.headers,
                    params={"status": status} if status else {}
                )
                
                if response.status_code != 200:
                    logger.error(f"Failed to get organization invitations: {response.text}")
                    return []
                
                invitations = response.json()
                formatted_invitations = []
                
                for invitation in invitations:
                    metadata = invitation.get("private_metadata", {})
                    formatted_invitations.append({
                        "invitation_id": invitation["id"],
                        "email_address": invitation["email_address"],
                        "status": invitation["status"],
                        "expires_at": invitation.get("expires_at"),
                        "created_at": invitation.get("created_at"),
                        "metadata": metadata
                    })
                
                return formatted_invitations
                
        except Exception as e:
            logger.error(f"Error getting organization invitations: {str(e)}")
            return []