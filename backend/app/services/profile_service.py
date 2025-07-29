from typing import Optional, Dict, Any
from app.models.profile import Profile, CoachData, ClientData
from app.repositories.profile_repository import ProfileRepository
from app.services.user_service import UserService
from app.services.clerk_organization_service import ClerkOrganizationService
import logging

logger = logging.getLogger(__name__)


class ProfileService:
    def __init__(self):
        self.profile_repository = ProfileRepository()
        self.user_service = UserService()
        self.clerk_org_service = ClerkOrganizationService()

    async def create_profile(self, clerk_user_id: str, profile_data: Dict[str, Any]) -> Profile:
        """Create a new profile for a user"""
        try:
            # Check if profile already exists
            existing_profile = await self.profile_repository.get_profile_by_clerk_id(clerk_user_id)
            if existing_profile:
                logger.info(f"Profile for user {clerk_user_id} already exists")
                return existing_profile

            # Validate role-specific data
            coach_data = None
            client_data = None
            
            if "coach_data" in profile_data and profile_data["coach_data"] is not None:
                coach_data = CoachData(**profile_data["coach_data"])
            elif "client_data" in profile_data and profile_data["client_data"] is not None:
                client_data = ClientData(**profile_data["client_data"])

            # Create profile
            profile = Profile(
                user_id=clerk_user_id, # This field will be deprecated
                clerk_user_id=clerk_user_id,
                first_name=profile_data.get("first_name", ""),
                last_name=profile_data.get("last_name", ""),
                coach_data=coach_data,
                client_data=client_data,
                primary_organization_id=profile_data.get("primary_organization_id")
            )

            created_profile = await self.profile_repository.create_profile(profile)
            logger.info(f"Created profile for user {clerk_user_id}")
            return created_profile

        except Exception as e:
            logger.error(f"Error creating profile: {e}")
            raise

    async def get_profile_by_clerk_id(self, clerk_user_id: str) -> Optional[Profile]:
        """Get profile by Clerk user ID"""
        try:
            # First try to get profile directly by clerk_user_id
            profile = await self.profile_repository.get_profile_by_clerk_id(clerk_user_id)
            if profile:
                return profile
            
            return None
        except Exception as e:
            logger.error(f"Error getting profile by Clerk ID {clerk_user_id}: {e}")
            raise

    async def update_profile(self, clerk_user_id: str, update_data: Dict[str, Any]) -> Optional[Profile]:
        """Update profile by Clerk user ID"""
        try:
            # Validate and prepare update data
            validated_data = {}
            
            # Basic fields
            if "first_name" in update_data:
                validated_data["first_name"] = update_data["first_name"]
            if "last_name" in update_data:
                validated_data["last_name"] = update_data["last_name"]

            # Role-specific data
            organizations = await self.clerk_org_service.get_user_organizations(clerk_user_id)
            primary_role = None
            if organizations:
                primary_role = organizations[0].get("role")

            if primary_role == "coach" and "coach_data" in update_data:
                coach_data = CoachData(**update_data["coach_data"])
                validated_data["coach_data"] = coach_data.dict()
            elif primary_role == "client" and "client_data" in update_data:
                client_data = ClientData(**update_data["client_data"])
                validated_data["client_data"] = client_data.dict()

            updated_profile = await self.profile_repository.update_profile_by_clerk_id(clerk_user_id, validated_data)
            if updated_profile:
                logger.info(f"Updated profile for user {clerk_user_id}")
            return updated_profile

        except Exception as e:
            logger.error(f"Error updating profile: {e}")
            raise

    async def delete_profile(self, clerk_user_id: str) -> bool:
        """Delete profile by Clerk user ID"""
        try:
            result = await self.profile_repository.delete_profile_by_clerk_id(clerk_user_id)
            if result:
                logger.info(f"Deleted profile for user {clerk_user_id}")
            return result

        except Exception as e:
            logger.error(f"Error deleting profile: {e}")
            raise

    async def profile_exists(self, clerk_user_id: str) -> bool:
        """Check if profile exists for user"""
        try:
            return await self.profile_repository.profile_exists_by_clerk_id(clerk_user_id)
        except Exception as e:
            logger.error(f"Error checking profile existence: {e}")
            raise

    async def sync_user_role_from_clerk(self, clerk_user_id: str) -> Optional[Profile]:
        """Synchronize user role from Clerk organization memberships."""
        try:
            organizations = await self.clerk_org_service.get_user_organizations(clerk_user_id)
            
            # Determine primary role: 'coach' takes precedence
            primary_role = "member" # Default role
            if any(org.get("role") == "coach" for org in organizations):
                primary_role = "coach"
            elif organizations:
                primary_role = organizations[0].get("role", "member")

            # Update Clerk user's public metadata
            clerk_user = self.user_service.get_user(clerk_user_id)
            if clerk_user:
                updated_metadata = clerk_user.public_metadata or {}
                updated_metadata["primary_role"] = primary_role
                
                # Also update organization roles in metadata
                org_roles = {org["id"]: {"role": org["role"]} for org in organizations}
                updated_metadata["organization_roles"] = org_roles

                from clerk_backend_api.services.users import Users
                Users().update_user(user_id=clerk_user_id, public_metadata=updated_metadata)
                logger.info(f"Updated Clerk public_metadata for user {clerk_user_id} with role '{primary_role}' and orgs.")

            # Prepare data for local profile update
            update_data = {
                "coach_data": None,
                "client_data": None,
            }
            if primary_role == "coach":
                update_data["coach_data"] = {}
            elif primary_role == "client":
                update_data["client_data"] = {}

            # Atomically update the local profile
            updated_profile = await self.profile_repository.update_profile_by_clerk_id(clerk_user_id, update_data)
            if updated_profile:
                logger.info(f"Successfully synced local profile for user {clerk_user_id} to '{primary_role}'.")
                return updated_profile
            else:
                logger.info(f"Profile for user {clerk_user_id} not found. Creating a new profile.")
                public_user_data = organizations[0].get("public_user_data", {}) if organizations else {}
                profile_data = {
                    "first_name": public_user_data.get("first_name", ""),
                    "last_name": public_user_data.get("last_name", ""),
                    "coach_data": CoachData().dict() if primary_role == "coach" else None,
                    "client_data": ClientData().dict() if primary_role == "client" else None,
                }
                return await self.create_profile(clerk_user_id, profile_data)

        except Exception as e:
            logger.error(f"Error syncing user role from Clerk for user {clerk_user_id}: {e}")
            raise