"""
Sprint S11.1 User Role Migration to Clerk Metadata

This script migrates user roles from the local approved_users.json file to Clerk's publicMetadata.
This is part of making Clerk the single source of truth for user roles and org permissions.

The script:
1. Reads user roles from backend/config/approved_users.json
2. Maps old roles to new standardized structure:
   - "client" -> "member"
   - "coach" -> "coach" 
   - "admin" -> "admin"
3. Updates each user's publicMetadata in Clerk with the new role structure
4. Assigns admin users to the Arete organization
5. Is idempotent - safe to run multiple times

Usage:
    python -m backend.migrations.s11_1_migrate_users_to_clerk_metadata migrate
    python -m backend.migrations.s11_1_migrate_users_to_clerk_metadata dry_run
    python -m backend.migrations.s11_1_migrate_users_to_clerk_metadata validate
"""

import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add the backend directory to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.core.config import settings

# Import Clerk SDK
try:
    from clerk_backend_api import Clerk, SDKError
    from clerk_backend_api.models import GetUserListRequest
except ImportError:
    print("❌ Clerk SDK not found. Please install with: pip install clerk-backend-api")
    sys.exit(1)

logger = logging.getLogger(__name__)

# Constants
ARETE_ORG_ID = "org_2znowNXOu9Flxs42iQFFl2joDRx"

# Role mapping from old to new structure
ROLE_MAPPING = {
    "client": "member",
    "coach": "coach", 
    "admin": "admin"
}

# Admin permissions for organization roles
ADMIN_PERMISSIONS = ["manage_users", "manage_content", "view_analytics"]


class ClerkUserRoleMigration:
    """Migration class to move user roles from JSON to Clerk metadata"""
    
    def __init__(self):
        self.clerk_client = None
        self.approved_users_path = Path(__file__).parent.parent / "config" / "approved_users.json"
        self.migration_stats = {
            "total_users": 0,
            "processed": 0,
            "skipped": 0,
            "errors": 0,
            "error_details": []
        }
    
    def initialize_clerk_client(self):
        """Initialize the Clerk client with API key from environment"""
        try:
            if not settings.clerk_secret_key:
                raise ValueError("CLERK_SECRET_KEY environment variable is required")
            
            # Initialize Clerk client
            self.clerk_client = Clerk(bearer_auth=settings.clerk_secret_key)
            logger.info("✅ Clerk client initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Clerk client: {e}")
            raise
    
    def load_approved_users(self) -> List[Dict[str, Any]]:
        """Load users from the approved_users.json file"""
        try:
            if not self.approved_users_path.exists():
                logger.error(f"❌ Approved users file not found: {self.approved_users_path}")
                return []
            
            with open(self.approved_users_path, 'r') as f:
                users = json.load(f)
            
            logger.info(f"✅ Loaded {len(users)} users from approved_users.json")
            return users
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Error parsing approved_users.json: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ Error reading approved_users.json: {e}")
            return []
    
    def map_role_to_new_structure(self, old_role: str) -> str:
        """Map old role to new standardized role"""
        return ROLE_MAPPING.get(old_role, old_role)
    
    def create_new_metadata_structure(self, old_role: str, user_email: str) -> Dict[str, Any]:
        """Create the new publicMetadata structure for a user"""
        primary_role = self.map_role_to_new_structure(old_role)
        
        metadata = {
            "primary_role": primary_role,
            "organization_roles": {}
        }
        
        # For admin users, assign them to the Arete organization
        if primary_role == "admin":
            metadata["default_org_id"] = ARETE_ORG_ID
            metadata["organization_roles"][ARETE_ORG_ID] = {
                "role": "admin",
                "permissions": ADMIN_PERMISSIONS
            }
        
        return metadata
    
    def is_metadata_already_migrated(self, current_metadata: Dict[str, Any]) -> bool:
        """Check if user's metadata already has the new structure"""
        if not current_metadata:
            return False
        
        # Check if the new structure fields exist
        required_fields = ["primary_role"]
        return all(field in current_metadata for field in required_fields)
    
    def _retry_with_backoff(self, func, operation_name: str, max_retries: int = 3):
        """Retry a function with exponential backoff for rate limiting"""
        for attempt in range(max_retries):
            try:
                return func()
            except SDKError as e:
                if hasattr(e, 'status_code') and e.status_code == 429 and attempt < max_retries - 1:
                    wait_time = (2 ** attempt) + 1  # Exponential backoff: 2, 4, 8 seconds
                    logger.warning(f"⚠️  Rate limited for {operation_name}, retrying in {wait_time} seconds... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                else:
                    raise  # Re-raise if not rate limit or max retries reached
        
        return None  # Should not reach here, but safety fallback
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user from Clerk by email address"""
        try:
            # Use the users list endpoint with email filter
            request = GetUserListRequest(email_address=[email])
            users = self.clerk_client.users.list(request=request)
            
            if users and len(users) > 0:
                # Convert the user object to dict for easier handling
                user = users[0]
                return {
                    "id": user.id,
                    "email_addresses": user.email_addresses,
                    "public_metadata": user.public_metadata or {}
                }
            
            logger.warning(f"⚠️  User not found in Clerk: {email}")
            return None
            
        except SDKError as e:
            # Handle rate limiting with exponential backoff
            if hasattr(e, 'status_code') and e.status_code == 429:
                return self._retry_with_backoff(lambda: self.get_user_by_email(email), f"get user {email}")
            
            logger.error(f"❌ Clerk API error getting user {email}: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Error getting user {email}: {e}")
            return None
    
    def update_user_metadata(self, user_id: str, new_metadata: Dict[str, Any]) -> bool:
        """Update user's publicMetadata in Clerk"""
        try:
            # Update the user's public metadata
            self.clerk_client.users.update(
                user_id=user_id,
                public_metadata=new_metadata
            )
            
            logger.info(f"✅ Updated metadata for user {user_id}")
            return True
            
        except SDKError as e:
            # Handle rate limiting with exponential backoff
            if hasattr(e, 'status_code') and e.status_code == 429:
                return self._retry_with_backoff(lambda: self.update_user_metadata(user_id, new_metadata), f"update user {user_id}")
            
            logger.error(f"❌ Clerk API error updating user {user_id}: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Error updating user {user_id}: {e}")
            return False
    
    def invalidate_user_sessions(self, user_id: str, email: str) -> bool:
        """Refresh user sessions by revoking active sessions after role update"""
        try:
            # Get all active sessions for the user
            sessions = self.clerk_client.users.get_user_sessions(user_id=user_id)
            logger.info(f"📱 Found {len(sessions)} active sessions for user {email}")
            
            if not sessions:
                logger.info(f"ℹ️ No active sessions found for {email} - no refresh needed")
                return True
            
            # Revoke all active sessions to force refresh
            revoked_count = 0
            for session in sessions:
                try:
                    self.clerk_client.sessions.revoke_session(session_id=session.id)
                    revoked_count += 1
                    logger.info(f"🔄 Revoked session {session.id} for {email}")
                except Exception as revoke_error:
                    logger.warning(f"⚠️ Failed to revoke session {session.id} for {email}: {revoke_error}")
            
            logger.info(f"✅ Successfully revoked {revoked_count} sessions for {email}")
            return True
            
        except SDKError as e:
            # Handle rate limiting with exponential backoff
            if hasattr(e, 'status_code') and e.status_code == 429:
                return self._retry_with_backoff(lambda: self.invalidate_user_sessions(user_id, email), f"refresh sessions for {email}")
            
            # Fallback to ban/unban approach if session revocation fails
            logger.warning(f"⚠️ Session revocation failed for {email}, falling back to ban/unban: {e}")
            try:
                self.clerk_client.users.ban(user_id=user_id)
                logger.info(f"🔒 Banned user {email} (fallback)")
                time.sleep(1)
                self.clerk_client.users.unban(user_id=user_id)
                logger.info(f"🔓 Unbanned user {email} (fallback) - sessions invalidated")
                return True
            except Exception as fallback_error:
                logger.error(f"❌ Fallback session invalidation failed for {email}: {fallback_error}")
                return False
            
        except Exception as e:
            logger.error(f"❌ Error refreshing sessions for {email}: {e}")
            return False
    
    def migrate_user_role(self, user_data: Dict[str, Any]) -> bool:
        """Migrate a single user's role to Clerk metadata"""
        email = user_data.get("email")
        old_role = user_data.get("role")
        
        if not email or not old_role:
            logger.error(f"❌ Invalid user data: {user_data}")
            return False
        
        logger.info(f"🔄 Processing user: {email} (role: {old_role})")
        
        # Get user from Clerk
        clerk_user = self.get_user_by_email(email)
        if not clerk_user:
            logger.error(f"❌ User {email} not found in Clerk - skipping")
            self.migration_stats["errors"] += 1
            self.migration_stats["error_details"].append(f"User not found in Clerk: {email}")
            return False
        
        user_id = clerk_user.get("id")
        current_metadata = clerk_user.get("public_metadata", {})
        
        # Check if already migrated (idempotency)
        if self.is_metadata_already_migrated(current_metadata):
            logger.info(f"⏭️  User {email} already has new metadata structure - skipping")
            self.migration_stats["skipped"] += 1
            return True
        
        # Create new metadata structure
        new_metadata = self.create_new_metadata_structure(old_role, email)
        
        # Merge with existing metadata to preserve other fields
        merged_metadata = {**current_metadata, **new_metadata}
        
        # Update user in Clerk
        if self.update_user_metadata(user_id, merged_metadata):
            logger.info(f"✅ Successfully migrated {email}: {old_role} -> {new_metadata['primary_role']}")
            
            # Force session invalidation after role update
            if self.invalidate_user_sessions(user_id, email):
                logger.info(f"✅ Successfully invalidated sessions for {email}")
            else:
                logger.warning(f"⚠️ Failed to invalidate sessions for {email} - user may need to sign out/in")
            
            self.migration_stats["processed"] += 1
            return True
        else:
            logger.error(f"❌ Failed to update metadata for {email}")
            self.migration_stats["errors"] += 1
            self.migration_stats["error_details"].append(f"Failed to update metadata: {email}")
            return False
    
    def dry_run_user_role(self, user_data: Dict[str, Any]) -> bool:
        """Simulate migrating a single user's role without making changes"""
        email = user_data.get("email")
        old_role = user_data.get("role")
        
        if not email or not old_role:
            logger.error(f"❌ [DRY RUN] Invalid user data: {user_data}")
            return False
        
        logger.info(f"🔍 [DRY RUN] Processing user: {email} (role: {old_role})")
        
        # Get user from Clerk
        clerk_user = self.get_user_by_email(email)
        if not clerk_user:
            logger.error(f"❌ [DRY RUN] User {email} not found in Clerk - would skip")
            self.migration_stats["errors"] += 1
            self.migration_stats["error_details"].append(f"User not found in Clerk: {email}")
            return False
        
        current_metadata = clerk_user.get("public_metadata", {})
        
        # Check if already migrated (idempotency)
        if self.is_metadata_already_migrated(current_metadata):
            logger.info(f"⏭️  [DRY RUN] User {email} already has new metadata structure - would skip")
            self.migration_stats["skipped"] += 1
            return True
        
        # Create new metadata structure
        new_metadata = self.create_new_metadata_structure(old_role, email)
        merged_metadata = {**current_metadata, **new_metadata}
        
        logger.info(f"✅ [DRY RUN] Would migrate {email}: {old_role} -> {new_metadata['primary_role']}")
        logger.info(f"📝 [DRY RUN] New metadata would be: {merged_metadata}")
        
        self.migration_stats["processed"] += 1
        return True
    
    def run_migration(self, dry_run: bool = False):
        """Run the complete migration process"""
        mode_text = "DRY RUN" if dry_run else "LIVE MIGRATION"
        logger.info(f"🚀 Starting user role migration to Clerk metadata ({mode_text})")
        
        try:
            # Initialize Clerk client
            self.initialize_clerk_client()
            
            # Load users from JSON file
            approved_users = self.load_approved_users()
            if not approved_users:
                logger.error("❌ No users to migrate")
                return
            
            self.migration_stats["total_users"] = len(approved_users)
            logger.info(f"📊 Found {len(approved_users)} users to process")
            
            # Process each user
            for user_data in approved_users:
                try:
                    if dry_run:
                        self.dry_run_user_role(user_data)
                    else:
                        self.migrate_user_role(user_data)
                except Exception as e:
                    email = user_data.get("email", "unknown")
                    logger.error(f"❌ Error processing user {email}: {e}")
                    self.migration_stats["errors"] += 1
                    self.migration_stats["error_details"].append(f"Processing error for {email}: {str(e)}")
            
            # Print final statistics
            self.print_migration_summary(dry_run)
            
            if dry_run:
                logger.info("🎯 Dry run completed - no changes made!")
            else:
                logger.info("🎉 Migration completed!")
            
        except Exception as e:
            logger.error(f"💥 Migration failed: {e}")
            raise
    
    def validate_migration(self):
        """Validate that the migration was successful"""
        logger.info("🔍 Validating migration results")
        
        try:
            # Initialize Clerk client
            self.initialize_clerk_client()
            
            # Load users from JSON file
            approved_users = self.load_approved_users()
            if not approved_users:
                logger.error("❌ No users to validate")
                return
            
            validation_stats = {
                "total_users": len(approved_users),
                "correctly_migrated": 0,
                "missing_users": 0,
                "incorrect_metadata": 0,
                "validation_errors": []
            }
            
            logger.info(f"📊 Validating {len(approved_users)} users")
            
            for user_data in approved_users:
                email = user_data.get("email")
                expected_role = self.map_role_to_new_structure(user_data.get("role"))
                
                # Get user from Clerk
                clerk_user = self.get_user_by_email(email)
                if not clerk_user:
                    logger.warning(f"⚠️  User not found in Clerk: {email}")
                    validation_stats["missing_users"] += 1
                    validation_stats["validation_errors"].append(f"User not found: {email}")
                    continue
                
                current_metadata = clerk_user.get("public_metadata", {})
                actual_role = current_metadata.get("primary_role")
                
                if actual_role == expected_role and self.is_metadata_already_migrated(current_metadata):
                    logger.info(f"✅ {email}: correctly migrated to {actual_role}")
                    validation_stats["correctly_migrated"] += 1
                else:
                    logger.error(f"❌ {email}: expected {expected_role}, got {actual_role}")
                    validation_stats["incorrect_metadata"] += 1
                    validation_stats["validation_errors"].append(
                        f"Incorrect metadata for {email}: expected {expected_role}, got {actual_role}"
                    )
            
            # Print validation summary
            logger.info("=== VALIDATION SUMMARY ===")
            logger.info(f"Total users: {validation_stats['total_users']}")
            logger.info(f"✅ Correctly migrated: {validation_stats['correctly_migrated']}")
            logger.info(f"⚠️  Missing users: {validation_stats['missing_users']}")
            logger.info(f"❌ Incorrect metadata: {validation_stats['incorrect_metadata']}")
            
            if validation_stats["validation_errors"]:
                logger.info("Validation errors:")
                for error in validation_stats["validation_errors"]:
                    logger.info(f"  - {error}")
            
            success_rate = (validation_stats["correctly_migrated"] / validation_stats["total_users"]) * 100
            logger.info(f"📊 Success rate: {success_rate:.1f}%")
            
            if success_rate == 100:
                logger.info("🎉 ✅ All users successfully validated!")
            elif success_rate >= 80:
                logger.info("⚠️ ✅ Most users validated successfully with some issues")
            else:
                logger.info("❌ 🚨 Significant validation issues encountered")
            
        except Exception as e:
            logger.error(f"💥 Validation failed: {e}")
            raise
    
    def print_migration_summary(self, dry_run: bool = False):
        """Print a summary of the migration results"""
        stats = self.migration_stats
        mode_text = "DRY RUN" if dry_run else "MIGRATION"
        
        logger.info(f"=== {mode_text} SUMMARY ===")
        logger.info(f"Total users: {stats['total_users']}")
        logger.info(f"✅ Successfully processed: {stats['processed']}")
        logger.info(f"⏭️  Skipped (already migrated): {stats['skipped']}")
        logger.info(f"❌ Errors: {stats['errors']}")
        
        if stats["error_details"]:
            logger.info("Error details:")
            for error in stats["error_details"]:
                logger.info(f"  - {error}")
        
        success_rate = ((stats["processed"] + stats["skipped"]) / stats["total_users"]) * 100 if stats["total_users"] > 0 else 0
        logger.info(f"📊 Success rate: {success_rate:.1f}%")
        
        # Final status emoji
        if success_rate == 100:
            logger.info("🎉 ✅ All operations completed successfully!")
        elif success_rate >= 80:
            logger.info("⚠️ ✅ Most operations completed successfully with some issues")
        else:
            logger.info("❌ 🚨 Significant issues encountered during processing")


def main():
    """Main function to run migration commands"""
    import argparse
    
    parser = argparse.ArgumentParser(description="User Role Migration to Clerk Metadata")
    parser.add_argument("command", choices=["migrate", "dry_run", "validate"], 
                       help="Migration command to run")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    migration = ClerkUserRoleMigration()
    
    try:
        if args.command == "migrate":
            migration.run_migration(dry_run=False)
        elif args.command == "dry_run":
            migration.run_migration(dry_run=True)
        elif args.command == "validate":
            migration.validate_migration()
            
    except Exception as e:
        logger.error(f"Command failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()