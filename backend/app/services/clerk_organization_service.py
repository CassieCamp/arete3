from typing import Optional, Dict, Any, List
import httpx
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class ClerkOrganizationService:
    """Service for managing Clerk organizations with business metadata"""
    
    def __init__(self):
        self.base_url = "https://api.clerk.com/v1"
        self.headers = {
            "Authorization": f"Bearer {settings.clerk_secret_key}",
            "Content-Type": "application/json"
        }
    
    async def create_coach_organization(self, coach_user_id: str, org_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create coach organization in Clerk with metadata"""
        try:
            # Prepare organization metadata
            metadata = {
                "organization_type": "coach_practice",
                "industry": org_data.get("industry", "Professional Coaching"),
                "website": org_data.get("website"),
                "description": org_data.get("description"),
                "is_solo_practice": org_data.get("is_solo_practice", True),
                "specialties": org_data.get("specialties", []),
                "created_by_profile_id": coach_user_id
            }
            
            # Create organization in Clerk
            async with httpx.AsyncClient() as client:
                # Create organization
                org_response = await client.post(
                    f"{self.base_url}/organizations",
                    headers=self.headers,
                    json={
                        "name": org_data["name"],
                        "created_by": coach_user_id,
                        "private_metadata": metadata
                    }
                )
                
                if org_response.status_code != 200:
                    logger.error(f"Failed to create organization: {org_response.text}")
                    raise Exception(f"Failed to create organization: {org_response.status_code}")
                
                clerk_org = org_response.json()
                
                # Add coach as admin member
                membership_response = await client.post(
                    f"{self.base_url}/organization_memberships",
                    headers=self.headers,
                    json={
                        "organization_id": clerk_org["id"],
                        "user_id": coach_user_id,
                        "role": "admin"
                    }
                )
                
                if membership_response.status_code != 200:
                    logger.error(f"Failed to add coach as admin: {membership_response.text}")
                    # Note: Organization was created, but membership failed
                
                return {
                    "id": clerk_org["id"],
                    "name": clerk_org["name"],
                    "created_at": clerk_org["created_at"],
                    "metadata": metadata,
                    "membership_role": "admin"
                }
                
        except Exception as e:
            logger.error(f"Error creating coach organization: {str(e)}")
            raise
    
    async def create_client_organization(self, client_user_id: str, org_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create client organization in Clerk with metadata"""
        try:
            # Prepare organization metadata
            metadata = {
                "organization_type": "client_company",
                "industry": org_data.get("industry"),
                "size": org_data.get("size"),
                "department": org_data.get("department"),
                "created_by_profile_id": client_user_id
            }
            
            # Create organization in Clerk
            async with httpx.AsyncClient() as client:
                # Create organization
                org_response = await client.post(
                    f"{self.base_url}/organizations",
                    headers=self.headers,
                    json={
                        "name": org_data["name"],
                        "created_by": client_user_id,
                        "private_metadata": metadata
                    }
                )
                
                if org_response.status_code != 200:
                    logger.error(f"Failed to create client organization: {org_response.text}")
                    raise Exception(f"Failed to create client organization: {org_response.status_code}")
                
                clerk_org = org_response.json()
                
                # Add client as admin member
                membership_response = await client.post(
                    f"{self.base_url}/organization_memberships",
                    headers=self.headers,
                    json={
                        "organization_id": clerk_org["id"],
                        "user_id": client_user_id,
                        "role": "admin"
                    }
                )
                
                if membership_response.status_code != 200:
                    logger.error(f"Failed to add client as admin: {membership_response.text}")
                
                return {
                    "id": clerk_org["id"],
                    "name": clerk_org["name"],
                    "created_at": clerk_org["created_at"],
                    "metadata": metadata,
                    "membership_role": "admin"
                }
                
        except Exception as e:
            logger.error(f"Error creating client organization: {str(e)}")
            raise
    
    async def get_organization_with_metadata(self, org_id: str) -> Optional[Dict[str, Any]]:
        """Get organization with business metadata"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/organizations/{org_id}",
                    headers=self.headers
                )
                
                if response.status_code == 404:
                    return None
                
                if response.status_code != 200:
                    logger.error(f"Failed to get organization: {response.text}")
                    raise Exception(f"Failed to get organization: {response.status_code}")
                
                org = response.json()
                return {
                    "id": org["id"],
                    "name": org["name"],
                    "created_at": org["created_at"],
                    "metadata": org.get("private_metadata", {})
                }
                
        except Exception as e:
            logger.error(f"Error getting organization: {str(e)}")
            raise
    
    async def update_organization_metadata(self, org_id: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Update organization metadata"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    f"{self.base_url}/organizations/{org_id}",
                    headers=self.headers,
                    json={
                        "private_metadata": metadata
                    }
                )
                
                if response.status_code != 200:
                    logger.error(f"Failed to update organization metadata: {response.text}")
                    raise Exception(f"Failed to update organization metadata: {response.status_code}")
                
                return response.json()
                
        except Exception as e:
            logger.error(f"Error updating organization metadata: {str(e)}")
            raise
    
    async def get_user_organizations(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all organizations for a user"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/users/{user_id}/organization_memberships",
                    headers=self.headers
                )
                
                if response.status_code != 200:
                    logger.error(f"Failed to get user organizations: {response.text}")
                    raise Exception(f"Failed to get user organizations: {response.status_code}")
                
                memberships = response.json()
                organizations = []
                
                for membership in memberships:
                    org = membership.get("organization", {})
                    organizations.append({
                        "id": org.get("id"),
                        "name": org.get("name"),
                        "role": membership.get("role"),
                        "metadata": org.get("private_metadata", {})
                    })
                
                return organizations
                
        except Exception as e:
            logger.error(f"Error getting user organizations: {str(e)}")
            raise
    
    async def get_organization_members(self, org_id: str) -> List[Dict[str, Any]]:
        """Get all members of an organization"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/organizations/{org_id}/memberships",
                    headers=self.headers
                )
                
                if response.status_code != 200:
                    logger.error(f"Failed to get organization members: {response.text}")
                    raise Exception(f"Failed to get organization members: {response.status_code}")
                
                memberships = response.json()
                members = []
                
                for membership in memberships:
                    user = membership.get("public_user_data", {})
                    members.append({
                        "user_id": user.get("user_id"),
                        "first_name": user.get("first_name"),
                        "last_name": user.get("last_name"),
                        "email": user.get("email_addresses", [{}])[0].get("email_address"),
                        "role": membership.get("role"),
                        "joined_at": membership.get("created_at")
                    })
                
                return members
                
        except Exception as e:
            logger.error(f"Error getting organization members: {str(e)}")
            raise