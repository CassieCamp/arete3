from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.clerk_organization_service import ClerkOrganizationService
import logging

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self):
        self.user_repository = UserRepository()
        self.clerk_org_service = ClerkOrganizationService()

    async def create_user_from_clerk(self, clerk_user_id: str, email: str,
                                   primary_role: str = "member",
                                   organization_roles: Dict[str, Any] = None) -> User:
        """Create a new user from Clerk webhook data with standardized role structure"""
        logger.info(f"=== UserService.create_user_from_clerk called ===")
        logger.info(f"Parameters: clerk_user_id={clerk_user_id}, email={email}, primary_role={primary_role}")
        
        try:
            # Check if user already exists
            logger.info(f"Checking if user already exists with Clerk ID: {clerk_user_id}")
            existing_user = await self.user_repository.get_user_by_clerk_id(clerk_user_id)
            
            if existing_user:
                logger.info(f"✅ User with Clerk ID {clerk_user_id} already exists: {existing_user}")
                return existing_user
            
            logger.info("User does not exist, creating new user")
            
            # Create new user with standardized role structure
            user = User(
                clerk_user_id=clerk_user_id,
                email=email,
                primary_role=primary_role,
                organization_roles=organization_roles or {}
            )
            logger.info(f"Created User model instance: {user}")
            
            logger.info("Calling user_repository.create_user...")
            created_user = await self.user_repository.create_user(user)
            logger.info(f"✅ Successfully created new user: {created_user}")
            logger.info(f"Created user ID: {created_user.id}")
            return created_user
            
        except Exception as e:
            logger.error(f"❌ Error creating user from Clerk: {e}")
            logger.error(f"Exception type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
    

    async def get_user_by_clerk_id(self, clerk_user_id: str) -> Optional[User]:
        """Get user by Clerk user ID"""
        try:
            return await self.user_repository.get_user_by_clerk_id(clerk_user_id)
        except Exception as e:
            logger.error(f"Error getting user by Clerk ID {clerk_user_id}: {e}")
            raise

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        try:
            return await self.user_repository.get_user_by_email(email)
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {e}")
            raise

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        try:
            return await self.user_repository.get_user_by_id(user_id)
        except Exception as e:
            logger.error(f"Error getting user by ID {user_id}: {e}")
            raise

    async def update_user_role(self, clerk_user_id: str, primary_role: str) -> Optional[User]:
        """Update user primary role (deprecated - roles should be managed via Clerk)"""
        logger.warning("⚠️ update_user_role is deprecated - roles should be managed via Clerk publicMetadata")
        try:
            user = await self.user_repository.get_user_by_clerk_id(clerk_user_id)
            if not user:
                logger.warning(f"User with Clerk ID {clerk_user_id} not found")
                return None

            return await self.user_repository.update_user(str(user.id), {"primary_role": primary_role})
        except Exception as e:
            logger.error(f"Error updating user role: {e}")
            raise

    async def delete_user(self, clerk_user_id: str) -> bool:
        """Delete user by Clerk ID"""
        try:
            user = await self.user_repository.get_user_by_clerk_id(clerk_user_id)
            if not user:
                logger.warning(f"User with Clerk ID {clerk_user_id} not found")
                return False

            return await self.user_repository.delete_user(str(user.id))
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            raise

    async def get_user_roles(self, clerk_user_id: str) -> Dict[str, Any]:
        """Get comprehensive role information for a user"""
        try:
            logger.info(f"🔍 DEBUG - get_user_roles called for clerk_user_id: {clerk_user_id}")
            
            user = await self.user_repository.get_user_by_clerk_id(clerk_user_id)
            if not user:
                logger.warning(f"🔍 DEBUG - User not found in database for clerk_user_id: {clerk_user_id}")
                return None
            
            logger.info(f"🔍 DEBUG - Found user in database: {user.email}")
            
            # Get organization roles from Clerk (if needed for additional context)
            logger.info(f"🔍 DEBUG - Fetching organization roles from Clerk...")
            clerk_organization_roles = await self.clerk_org_service.get_user_roles_in_organizations(clerk_user_id)
            logger.info(f"🔍 DEBUG - Organization roles from Clerk: {clerk_organization_roles}")
            
            # Get permissions based on roles
            logger.info(f"🔍 DEBUG - Fetching permissions from Clerk...")
            permissions = await self.clerk_org_service.get_user_permissions(clerk_user_id)
            logger.info(f"🔍 DEBUG - Permissions from Clerk: {permissions}")
            
            return {
                "user_id": str(user.id),
                "clerk_user_id": user.clerk_user_id,
                "email": user.email,
                "primary_role": user.primary_role,
                "organization_roles": user.organization_roles,  # From standardized structure
                "clerk_organization_roles": clerk_organization_roles,  # From Clerk API for comparison
                "permissions": permissions
            }
            
        except Exception as e:
            logger.error(f"Error getting user roles: {e}")
            raise

    async def add_organization_membership(self, clerk_user_id: str, org_id: str,
                                        role: str, org_type: str = "unknown") -> bool:
        """Add organization membership to user (deprecated - managed via Clerk)"""
        logger.warning("⚠️ add_organization_membership is deprecated - organization memberships should be managed via Clerk")
        logger.info(f"Organization membership for {clerk_user_id} in {org_id} should be managed through Clerk publicMetadata")
        return True  # Return success to avoid breaking existing flows

    async def remove_organization_membership(self, clerk_user_id: str, org_id: str) -> bool:
        """Remove organization membership from user (deprecated - managed via Clerk)"""
        logger.warning("⚠️ remove_organization_membership is deprecated - organization memberships should be managed via Clerk")
        logger.info(f"Organization membership removal for {clerk_user_id} from {org_id} should be managed through Clerk")
        return True  # Return success to avoid breaking existing flows

    async def update_user_role_in_organization(self, clerk_user_id: str, org_id: str, new_role: str) -> bool:
        """Update user's role in a specific organization (deprecated - managed via Clerk)"""
        logger.warning("⚠️ update_user_role_in_organization is deprecated - organization roles should be managed via Clerk")
        logger.info(f"Organization role update for {clerk_user_id} in {org_id} should be managed through Clerk publicMetadata")
        return True  # Return success to avoid breaking existing flows

    async def update_user_role_from_clerk(self, clerk_user_id: str,
                                        primary_role: str = None,
                                        organization_roles: Dict[str, Any] = None) -> Optional[User]:
        """Update user role data from Clerk publicMetadata"""
        try:
            user = await self.user_repository.get_user_by_clerk_id(clerk_user_id)
            if not user:
                logger.warning(f"User with Clerk ID {clerk_user_id} not found for role update")
                return None

            update_data = {"updated_at": datetime.utcnow()}
            
            # Update primary role if provided
            if primary_role:
                update_data["primary_role"] = primary_role
                logger.info(f"Updating primary role to: {primary_role}")
            
            # Update organization roles if provided
            if organization_roles is not None:
                update_data["organization_roles"] = organization_roles
                logger.info(f"Updating organization roles to: {organization_roles}")
            
            # Perform the update
            updated_user = await self.user_repository.update_user(str(user.id), update_data)
            
            if updated_user:
                logger.info(f"✅ Successfully updated user roles for: {clerk_user_id}")
            else:
                logger.warning(f"⚠️ Failed to update user roles for: {clerk_user_id}")
                
            return updated_user
            
        except Exception as e:
            logger.error(f"Error updating user role from Clerk: {e}")
            raise

    async def update_user_session_settings(self, clerk_user_id: str, session_auto_send_context: bool) -> Optional[User]:
        """Update user session settings"""
        logger.info(f"=== UserService.update_user_session_settings called ===")
        logger.info(f"clerk_user_id: {clerk_user_id}, session_auto_send_context: {session_auto_send_context}")
        
        try:
            updated_user = await self.user_repository.update_user_session_settings(
                clerk_user_id, session_auto_send_context
            )
            
            if updated_user:
                logger.info(f"✅ Successfully updated session settings for user: {clerk_user_id}")
            else:
                logger.warning(f"⚠️ Failed to update session settings for user: {clerk_user_id}")
                
            return updated_user
            
        except Exception as e:
            logger.error(f"Error updating user session settings: {e}")
            raise
