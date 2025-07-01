import json
import os
from typing import Optional, List, Dict, Any
from pathlib import Path
import logging
from datetime import datetime
import shutil

logger = logging.getLogger(__name__)


class RoleService:
    """Service for managing user role assignments based on approved users configuration."""
    
    def __init__(self):
        # Get the path to the config file relative to the project root
        self.config_path = Path(__file__).parent.parent.parent / "config" / "approved_users.json"
        self.backup_dir = Path(__file__).parent.parent.parent / "config" / "backups"
        logger.info(f"RoleService initialized with config path: {self.config_path}")
        
        # Ensure backup directory exists
        self.backup_dir.mkdir(exist_ok=True)
    
    def _load_approved_users(self) -> List[Dict[str, Any]]:
        """Load approved users from the configuration file."""
        try:
            if not self.config_path.exists():
                logger.warning(f"Approved users config file not found at: {self.config_path}")
                return []
            
            with open(self.config_path, 'r') as f:
                approved_users = json.load(f)
            
            logger.info(f"Loaded {len(approved_users)} approved users from config")
            return approved_users
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing approved users JSON: {e}")
            return []
        except Exception as e:
            logger.error(f"Error reading approved users config: {e}")
            return []
    
    def _save_approved_users(self, approved_users: List[Dict[str, Any]]) -> bool:
        """Save approved users to the configuration file with backup."""
        try:
            # Create backup before saving
            self._create_backup()
            
            # Write to temporary file first for atomic operation
            temp_path = self.config_path.with_suffix('.tmp')
            with open(temp_path, 'w') as f:
                json.dump(approved_users, f, indent=2, default=str)
            
            # Atomic move
            temp_path.replace(self.config_path)
            
            logger.info(f"Successfully saved {len(approved_users)} approved users to config")
            return True
            
        except Exception as e:
            logger.error(f"Error saving approved users config: {e}")
            return False
    
    def _create_backup(self) -> str:
        """Create a backup of the current configuration file."""
        try:
            if not self.config_path.exists():
                return ""
            
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            backup_path = self.backup_dir / f"approved_users_{timestamp}.json"
            
            shutil.copy2(self.config_path, backup_path)
            logger.info(f"Created backup at: {backup_path}")
            return str(backup_path)
            
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return ""
    
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
            
            approved_users = self._load_approved_users()
            
            # Search for the email (case-insensitive)
            email_lower = email.lower()
            for user in approved_users:
                if user.get("email", "").lower() == email_lower:
                    role = user.get("role")
                    logger.info(f"Found role '{role}' for email: {email}")
                    return role
            
            logger.info(f"No role found for email: {email}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting role for email {email}: {e}")
            return None
    
    def add_approved_user(self, email: str, role: str, approved_by: str = "admin", notes: str = "") -> bool:
        """
        Add a new approved user to the configuration.
        
        Args:
            email: The email address to add
            role: The role to assign ("coach" or "client")
            approved_by: Who approved this user
            notes: Optional notes about the approval
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Adding approved user: {email} with role: {role}")
            
            # Validate inputs
            if not email or not role:
                logger.error("Email and role are required")
                return False
            
            if role not in ["coach", "client"]:
                logger.error(f"Invalid role: {role}. Must be 'coach' or 'client'")
                return False
            
            approved_users = self._load_approved_users()
            
            # Check if user already exists
            email_lower = email.lower()
            for user in approved_users:
                if user.get("email", "").lower() == email_lower:
                    logger.warning(f"User {email} already exists in approved users")
                    return False
            
            # Add new user
            new_user = {
                "email": email.lower(),
                "role": role,
                "approved_at": datetime.utcnow().isoformat(),
                "approved_by": approved_by,
                "notes": notes,
                "status": "approved"
            }
            
            approved_users.append(new_user)
            
            # Save to file
            if self._save_approved_users(approved_users):
                logger.info(f"Successfully added approved user: {email}")
                return True
            else:
                logger.error(f"Failed to save approved user: {email}")
                return False
                
        except Exception as e:
            logger.error(f"Error adding approved user {email}: {e}")
            return False
    
    def remove_approved_user(self, email: str) -> bool:
        """
        Remove an approved user from the configuration.
        
        Args:
            email: The email address to remove
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Removing approved user: {email}")
            
            approved_users = self._load_approved_users()
            
            # Find and remove user
            email_lower = email.lower()
            original_count = len(approved_users)
            approved_users = [user for user in approved_users
                            if user.get("email", "").lower() != email_lower]
            
            if len(approved_users) == original_count:
                logger.warning(f"User {email} not found in approved users")
                return False
            
            # Save to file
            if self._save_approved_users(approved_users):
                logger.info(f"Successfully removed approved user: {email}")
                return True
            else:
                logger.error(f"Failed to save after removing user: {email}")
                return False
                
        except Exception as e:
            logger.error(f"Error removing approved user {email}: {e}")
            return False
    
    def update_approved_user(self, email: str, updates: Dict[str, Any]) -> bool:
        """
        Update an approved user's information.
        
        Args:
            email: The email address to update
            updates: Dictionary of fields to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Updating approved user: {email} with updates: {updates}")
            
            approved_users = self._load_approved_users()
            
            # Find and update user
            email_lower = email.lower()
            user_found = False
            
            for user in approved_users:
                if user.get("email", "").lower() == email_lower:
                    user_found = True
                    
                    # Update allowed fields
                    allowed_fields = ["role", "notes", "status", "approved_by"]
                    for field, value in updates.items():
                        if field in allowed_fields:
                            user[field] = value
                    
                    # Update timestamp
                    user["updated_at"] = datetime.utcnow().isoformat()
                    break
            
            if not user_found:
                logger.warning(f"User {email} not found in approved users")
                return False
            
            # Save to file
            if self._save_approved_users(approved_users):
                logger.info(f"Successfully updated approved user: {email}")
                return True
            else:
                logger.error(f"Failed to save after updating user: {email}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating approved user {email}: {e}")
            return False
    
    def get_all_approved_users(self) -> List[Dict[str, Any]]:
        """
        Get all approved users.
        
        Returns:
            List of approved user dictionaries
        """
        try:
            return self._load_approved_users()
        except Exception as e:
            logger.error(f"Error getting all approved users: {e}")
            return []
    
    def get_approved_user(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific approved user by email.
        
        Args:
            email: The email address to look up
            
        Returns:
            User dictionary if found, None otherwise
        """
        try:
            approved_users = self._load_approved_users()
            email_lower = email.lower()
            
            for user in approved_users:
                if user.get("email", "").lower() == email_lower:
                    return user
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting approved user {email}: {e}")
            return None
    
    def bulk_import_users(self, users: List[Dict[str, Any]], approved_by: str = "admin") -> Dict[str, Any]:
        """
        Bulk import approved users.
        
        Args:
            users: List of user dictionaries to import
            approved_by: Who approved these users
            
        Returns:
            Dictionary with import results
        """
        try:
            logger.info(f"Bulk importing {len(users)} users")
            
            results = {
                "success": 0,
                "failed": 0,
                "errors": []
            }
            
            for user_data in users:
                email = user_data.get("email")
                role = user_data.get("role")
                notes = user_data.get("notes", "")
                
                if self.add_approved_user(email, role, approved_by, notes):
                    results["success"] += 1
                else:
                    results["failed"] += 1
                    results["errors"].append(f"Failed to add user: {email}")
            
            logger.info(f"Bulk import completed: {results['success']} success, {results['failed']} failed")
            return results
            
        except Exception as e:
            logger.error(f"Error in bulk import: {e}")
            return {"success": 0, "failed": len(users), "errors": [str(e)]}
    
    def export_approved_users(self) -> List[Dict[str, Any]]:
        """
        Export all approved users for backup or migration.
        
        Returns:
            List of approved user dictionaries
        """
        try:
            return self._load_approved_users()
        except Exception as e:
            logger.error(f"Error exporting approved users: {e}")
            return []
    
    def restore_from_backup(self, backup_path: str) -> bool:
        """
        Restore approved users from a backup file.
        
        Args:
            backup_path: Path to the backup file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Restoring from backup: {backup_path}")
            
            backup_file = Path(backup_path)
            if not backup_file.exists():
                logger.error(f"Backup file not found: {backup_path}")
                return False
            
            # Create current backup before restore
            self._create_backup()
            
            # Copy backup to current config
            shutil.copy2(backup_file, self.config_path)
            
            logger.info(f"Successfully restored from backup: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error restoring from backup {backup_path}: {e}")
            return False