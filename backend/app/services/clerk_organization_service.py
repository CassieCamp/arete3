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
            logger.info(f"🔍 DEBUG - get_user_organizations called for user_id: {user_id}")
            
            async with httpx.AsyncClient() as client:
                url = f"{self.base_url}/users/{user_id}/organization_memberships"
                logger.info(f"🔍 DEBUG - Making request to: {url}")
                
                response = await client.get(url, headers=self.headers)
                
                logger.info(f"🔍 DEBUG - Response status: {response.status_code}")
                logger.info(f"🔍 DEBUG - Response text: {response.text}")
                
                if response.status_code != 200:
                    logger.error(f"Failed to get user organizations: {response.text}")
                    raise Exception(f"Failed to get user organizations: {response.status_code}")
                
                response_data = response.json()
                logger.info(f"🔍 DEBUG - Raw response data: {response_data}")
                
                # Handle Clerk API response format: {"data": [...], "total_count": N}
                if isinstance(response_data, dict) and "data" in response_data:
                    memberships = response_data["data"]
                elif isinstance(response_data, list):
                    memberships = response_data
                else:
                    logger.warning(f"Unexpected response format from Clerk API: {type(response_data)}")
                    return []
                
                organizations = []
                
                for membership in memberships:
                    try:
                        # Handle dict-based membership (which is what Clerk returns)
                        if isinstance(membership, dict):
                            org = membership.get("organization")
                            
                            if isinstance(org, dict):
                                # Clean up role format (remove "org:" prefix if present)
                                raw_role = membership.get("role", "member")
                                clean_role = raw_role.replace("org:", "") if raw_role else "member"
                                
                                logger.info(f"🔍 DEBUG - Processing organization: {org.get('name')}, role: {raw_role} -> {clean_role}")
                                
                                organizations.append({
                                    "id": org.get("id"),
                                    "name": org.get("name"),
                                    "role": clean_role,
                                    "metadata": org.get("private_metadata", {})
                                })
                            else:
                                logger.warning(f"Unexpected organization format in membership: {type(org)}")
                        else:
                            logger.warning(f"Unexpected membership type: {type(membership)}")
                                
                    except Exception as e:
                        logger.error(f"Error processing membership: {e}")
                        # Continue processing other memberships
                        continue
                
                logger.info(f"🔍 DEBUG - Final organizations list: {organizations}")
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
    
    async def add_user_to_organization(self, org_id: str, user_id: str, role: str = "basic_member") -> Dict[str, Any]:
        """Add a user to an organization with specified role"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/organization_memberships",
                    headers=self.headers,
                    json={
                        "organization_id": org_id,
                        "user_id": user_id,
                        "role": role
                    }
                )
                
                if response.status_code != 200:
                    logger.error(f"Failed to add user to organization: {response.text}")
                    raise Exception(f"Failed to add user to organization: {response.status_code}")
                
                membership = response.json()
                return {
                    "membership_id": membership.get("id"),
                    "organization_id": org_id,
                    "user_id": user_id,
                    "role": role,
                    "created_at": membership.get("created_at")
                }
                
        except Exception as e:
            logger.error(f"Error adding user to organization: {str(e)}")
            raise
    
    async def update_user_organization_role(self, membership_id: str, role: str) -> Dict[str, Any]:
        """Update a user's role in an organization"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    f"{self.base_url}/organization_memberships/{membership_id}",
                    headers=self.headers,
                    json={"role": role}
                )
                
                if response.status_code != 200:
                    logger.error(f"Failed to update user role: {response.text}")
                    raise Exception(f"Failed to update user role: {response.status_code}")
                
                return response.json()
                
        except Exception as e:
            logger.error(f"Error updating user organization role: {str(e)}")
            raise
    
    async def remove_user_from_organization(self, membership_id: str) -> bool:
        """Remove a user from an organization"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{self.base_url}/organization_memberships/{membership_id}",
                    headers=self.headers
                )
                
                if response.status_code not in [200, 204]:
                    logger.error(f"Failed to remove user from organization: {response.text}")
                    raise Exception(f"Failed to remove user from organization: {response.status_code}")
                
                return True
                
        except Exception as e:
            logger.error(f"Error removing user from organization: {str(e)}")
            raise
    
    async def get_user_roles_in_organizations(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all roles a user has across organizations"""
        try:
            organizations = await self.get_user_organizations(user_id)
            
            roles_info = []
            for org in organizations:
                org_details = await self.get_organization_with_metadata(org["id"])
                if org_details:
                    org_type = org_details.get("metadata", {}).get("organization_type", "unknown")
                    
                    roles_info.append({
                        "organization_id": org["id"],
                        "organization_name": org["name"],
                        "role": org["role"],
                        "org_type": org_type,
                        "metadata": org_details.get("metadata", {})
                    })
            
            return roles_info
            
        except Exception as e:
            logger.error(f"Error getting user roles in organizations: {str(e)}")
            raise
    
    async def get_user_permissions(self, user_id: str) -> List[str]:
        """Get all permissions for a user based on their organization roles"""
        try:
            roles_info = await self.get_user_roles_in_organizations(user_id)
            
            permissions = set()
            
            for role_info in roles_info:
                role = role_info["role"]
                org_type = role_info["org_type"]
                
                # Add permissions based on role and organization type
                if role == "admin":
                    if org_type == "coach_practice":
                        permissions.update([
                            "coaching_relationships:manage",
                            "client_data:read",
                            "resources:create",
                            "clients:invite",
                            "org_members:manage",
                            "org_settings:manage"
                        ])
                    elif org_type == "client_company":
                        permissions.update([
                            "org_members:manage",
                            "org_settings:manage",
                            "coaches:connect"
                        ])
                    else:  # Arete organization admin
                        permissions.update([
                            "platform:manage",
                            "users:manage",
                            "organizations:manage"
                        ])
                
                elif role == "coach":
                    permissions.update([
                        "coaching_relationships:manage",
                        "client_data:read",
                        "resources:create",
                        "clients:invite"
                    ])
                
                elif role == "basic_member" or role == "member":
                    permissions.update([
                        "profile:manage",
                        "goals:manage",
                        "progress:read"
                    ])
            
            return list(permissions)
            
        except Exception as e:
            logger.error(f"Error getting user permissions: {str(e)}")
            raise