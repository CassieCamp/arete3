from clerk_backend_api import Clerk, models
from app.core.config import settings
from app.schemas.user import UserResponse
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self):
        self.clerk_client = Clerk()

    def get_user(self, user_id: str) -> Optional[models.User]:
        """
        Get user data directly from Clerk.
        """
        try:
            # Note: The clerk-backend-api has inconsistent method names.
            # While get_user_list() works for emails, it fails for user_id.
            # The list() method is the correct one for querying by user_id.
            users = self.clerk_client.users.list(user_id=[user_id])
            if users and len(users) > 0:
                return users[0]
            return None
        except Exception as e:
            logger.error(f"Error fetching user from Clerk: {e}")
            return None

    def get_user_by_email(self, email: str) -> Optional[models.User]:
        """
        Get user data by email from Clerk.
        Note: This is a simplified example. In a real application, you might need to handle multiple users with the same email.
        """
        try:
            users = self.clerk_client.users.list(email_address=[email])
            if users and len(users) > 0:
                return users[0]
            return None
        except Exception as e:
            logger.error(f"Error fetching user by email from Clerk: {e}")
            return None

    def get_all_users(self) -> Optional[list[models.User]]:
        """
        Get all users from Clerk.
        """
        try:
            return self.clerk_client.users.list()
        except Exception as e:
            logger.error(f"Error fetching all users from Clerk: {e}")
            return None
