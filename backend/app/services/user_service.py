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
        logger.info(f"=== UserService.create_user_from_clerk called ===")
        logger.info(f"Parameters: clerk_user_id={clerk_user_id}, email={email}, role={role}")
        
        try:
            # Check if user already exists
            logger.info(f"Checking if user already exists with Clerk ID: {clerk_user_id}")
            existing_user = await self.user_repository.get_user_by_clerk_id(clerk_user_id)
            
            if existing_user:
                logger.info(f"✅ User with Clerk ID {clerk_user_id} already exists: {existing_user}")
                return existing_user
            
            logger.info("User does not exist, creating new user")

            # Create new user
            user = User(
                clerk_user_id=clerk_user_id,
                email=email,
                role=role
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

    async def get_onboarding_state(self, clerk_user_id: str) -> Optional[dict]:
        """Get user's onboarding state"""
        try:
            user = await self.user_repository.get_user_by_clerk_id(clerk_user_id)
            if not user:
                logger.warning(f"User with Clerk ID {clerk_user_id} not found")
                return None
            
            return user.onboarding_state
        except Exception as e:
            logger.error(f"Error getting onboarding state for user {clerk_user_id}: {e}")
            raise

    async def update_onboarding_state(self, clerk_user_id: str, onboarding_state: dict) -> Optional[User]:
        """Update user's onboarding state"""
        try:
            logger.info(f"=== UserService.update_onboarding_state called ===")
            logger.info(f"clerk_user_id: {clerk_user_id}, state: {onboarding_state}")
            
            user = await self.user_repository.get_user_by_clerk_id(clerk_user_id)
            if not user:
                logger.warning(f"User with Clerk ID {clerk_user_id} not found")
                return None

            # Update the onboarding state
            updated_user = await self.user_repository.update_user(
                str(user.id),
                {"onboarding_state": onboarding_state}
            )
            
            logger.info(f"✅ Updated onboarding state for user: {clerk_user_id}")
            return updated_user
        except Exception as e:
            logger.error(f"Error updating onboarding state for user {clerk_user_id}: {e}")
            raise

    async def start_onboarding(self, clerk_user_id: str) -> Optional[User]:
        """Start onboarding process for a user"""
        try:
            from datetime import datetime
            
            onboarding_state = {
                "completed": False,
                "current_step": 0,
                "steps_completed": [],
                "started_at": datetime.utcnow().isoformat(),
                "completed_at": None
            }
            
            return await self.update_onboarding_state(clerk_user_id, onboarding_state)
        except Exception as e:
            logger.error(f"Error starting onboarding for user {clerk_user_id}: {e}")
            raise

    async def complete_onboarding_step(self, clerk_user_id: str, step: int) -> Optional[User]:
        """Complete a specific onboarding step"""
        try:
            current_state = await self.get_onboarding_state(clerk_user_id)
            if not current_state:
                return None
            
            # Add step to completed steps if not already there
            if step not in current_state.get("steps_completed", []):
                current_state["steps_completed"].append(step)
            
            # Update current step to the next one
            current_state["current_step"] = max(current_state.get("current_step", 0), step + 1)
            
            return await self.update_onboarding_state(clerk_user_id, current_state)
        except Exception as e:
            logger.error(f"Error completing onboarding step {step} for user {clerk_user_id}: {e}")
            raise

    async def complete_onboarding(self, clerk_user_id: str) -> Optional[User]:
        """Mark onboarding as completed"""
        try:
            from datetime import datetime
            
            current_state = await self.get_onboarding_state(clerk_user_id)
            if not current_state:
                return None
            
            current_state["completed"] = True
            current_state["completed_at"] = datetime.utcnow().isoformat()
            
            return await self.update_onboarding_state(clerk_user_id, current_state)
        except Exception as e:
            logger.error(f"Error completing onboarding for user {clerk_user_id}: {e}")
            raise