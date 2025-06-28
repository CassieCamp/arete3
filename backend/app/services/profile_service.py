from typing import Optional, Dict, Any
from app.models.profile import Profile, CoachData, ClientData
from app.repositories.profile_repository import ProfileRepository
from app.services.user_service import UserService
import logging

logger = logging.getLogger(__name__)


class ProfileService:
    def __init__(self):
        self.profile_repository = ProfileRepository()
        self.user_service = UserService()

    async def create_profile(self, clerk_user_id: str, profile_data: Dict[str, Any]) -> Profile:
        """Create a new profile for a user"""
        try:
            # Get user by Clerk ID
            user = await self.user_service.get_user_by_clerk_id(clerk_user_id)
            if not user:
                raise ValueError(f"User with Clerk ID {clerk_user_id} not found")

            # Check if profile already exists
            existing_profile = await self.profile_repository.get_profile_by_user_id(str(user.id))
            if existing_profile:
                logger.info(f"Profile for user {user.id} already exists")
                return existing_profile

            # Validate role-specific data
            coach_data = None
            client_data = None
            
            if user.role == "coach" and "coach_data" in profile_data:
                coach_data = CoachData(**profile_data["coach_data"])
            elif user.role == "client" and "client_data" in profile_data:
                client_data = ClientData(**profile_data["client_data"])

            # Create profile
            profile = Profile(
                user_id=str(user.id),
                first_name=profile_data.get("first_name", ""),
                last_name=profile_data.get("last_name", ""),
                coach_data=coach_data,
                client_data=client_data
            )

            created_profile = await self.profile_repository.create_profile(profile)
            logger.info(f"Created profile for user {user.id}")
            return created_profile

        except Exception as e:
            logger.error(f"Error creating profile: {e}")
            raise

    async def get_profile_by_clerk_id(self, clerk_user_id: str) -> Optional[Profile]:
        """Get profile by Clerk user ID"""
        try:
            user = await self.user_service.get_user_by_clerk_id(clerk_user_id)
            if not user:
                return None

            return await self.profile_repository.get_profile_by_user_id(str(user.id))
        except Exception as e:
            logger.error(f"Error getting profile by Clerk ID {clerk_user_id}: {e}")
            raise

    async def update_profile(self, clerk_user_id: str, update_data: Dict[str, Any]) -> Optional[Profile]:
        """Update profile by Clerk user ID"""
        try:
            user = await self.user_service.get_user_by_clerk_id(clerk_user_id)
            if not user:
                raise ValueError(f"User with Clerk ID {clerk_user_id} not found")

            # Validate and prepare update data
            validated_data = {}
            
            # Basic fields
            if "first_name" in update_data:
                validated_data["first_name"] = update_data["first_name"]
            if "last_name" in update_data:
                validated_data["last_name"] = update_data["last_name"]

            # Role-specific data
            if user.role == "coach" and "coach_data" in update_data:
                coach_data = CoachData(**update_data["coach_data"])
                validated_data["coach_data"] = coach_data.dict()
            elif user.role == "client" and "client_data" in update_data:
                client_data = ClientData(**update_data["client_data"])
                validated_data["client_data"] = client_data.dict()

            updated_profile = await self.profile_repository.update_profile(str(user.id), validated_data)
            if updated_profile:
                logger.info(f"Updated profile for user {user.id}")
            return updated_profile

        except Exception as e:
            logger.error(f"Error updating profile: {e}")
            raise

    async def delete_profile(self, clerk_user_id: str) -> bool:
        """Delete profile by Clerk user ID"""
        try:
            user = await self.user_service.get_user_by_clerk_id(clerk_user_id)
            if not user:
                logger.warning(f"User with Clerk ID {clerk_user_id} not found")
                return False

            result = await self.profile_repository.delete_profile(str(user.id))
            if result:
                logger.info(f"Deleted profile for user {user.id}")
            return result

        except Exception as e:
            logger.error(f"Error deleting profile: {e}")
            raise

    async def profile_exists(self, clerk_user_id: str) -> bool:
        """Check if profile exists for user"""
        try:
            user = await self.user_service.get_user_by_clerk_id(clerk_user_id)
            if not user:
                return False

            return await self.profile_repository.profile_exists(str(user.id))
        except Exception as e:
            logger.error(f"Error checking profile existence: {e}")
            raise