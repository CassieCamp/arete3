from typing import Optional
from app.models.user import User
from app.repositories.user_repository import UserRepository
import logging

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self):
        self.user_repository = UserRepository()

    async def create_user_from_clerk(self, clerk_user_id: str, email: str, role: str) -> User:
        """Create a new user from Clerk webhook data"""
        try:
            # Check if user already exists
            existing_user = await self.user_repository.get_user_by_clerk_id(clerk_user_id)
            if existing_user:
                logger.info(f"User with Clerk ID {clerk_user_id} already exists")
                return existing_user

            # Create new user
            user = User(
                clerk_user_id=clerk_user_id,
                email=email,
                role=role
            )
            
            created_user = await self.user_repository.create_user(user)
            logger.info(f"Created new user with Clerk ID: {clerk_user_id}")
            return created_user
            
        except Exception as e:
            logger.error(f"Error creating user from Clerk: {e}")
            raise

    async def get_user_by_clerk_id(self, clerk_user_id: str) -> Optional[User]:
        """Get user by Clerk user ID"""
        try:
            return await self.user_repository.get_user_by_clerk_id(clerk_user_id)
        except Exception as e:
            logger.error(f"Error getting user by Clerk ID {clerk_user_id}: {e}")
            raise

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        try:
            return await self.user_repository.get_user_by_id(user_id)
        except Exception as e:
            logger.error(f"Error getting user by ID {user_id}: {e}")
            raise

    async def update_user_role(self, clerk_user_id: str, role: str) -> Optional[User]:
        """Update user role"""
        try:
            user = await self.user_repository.get_user_by_clerk_id(clerk_user_id)
            if not user:
                logger.warning(f"User with Clerk ID {clerk_user_id} not found")
                return None

            return await self.user_repository.update_user(str(user.id), {"role": role})
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