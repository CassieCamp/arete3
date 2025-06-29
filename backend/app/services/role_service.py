import json
import os
from typing import Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class RoleService:
    """Service for managing user role assignments based on approved users configuration."""
    
    def __init__(self):
        # Get the path to the config file relative to the project root
        self.config_path = Path(__file__).parent.parent.parent / "config" / "approved_users.json"
        logger.info(f"RoleService initialized with config path: {self.config_path}")
    
    def get_role_for_email(self, email: str) -> Optional[str]:
        """
        Get the role for a given email address from the approved users configuration.
        
        Args:
            email: The email address to look up (case-insensitive)
            
        Returns:
            The role string if found, None otherwise
        """
        try:
            logger.info(f"Looking up role for email: {email}")
            
            # Check if config file exists
            if not self.config_path.exists():
                logger.warning(f"Approved users config file not found at: {self.config_path}")
                return None
            
            # Read and parse the JSON file
            with open(self.config_path, 'r') as f:
                approved_users = json.load(f)
            
            logger.info(f"Loaded {len(approved_users)} approved users from config")
            
            # Search for the email (case-insensitive)
            email_lower = email.lower()
            for user in approved_users:
                if user.get("email", "").lower() == email_lower:
                    role = user.get("role")
                    logger.info(f"Found role '{role}' for email: {email}")
                    return role
            
            logger.info(f"No role found for email: {email}")
            return None
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing approved users JSON: {e}")
            return None
        except Exception as e:
            logger.error(f"Error reading approved users config: {e}")
            return None