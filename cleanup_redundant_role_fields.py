#!/usr/bin/env python3
"""
Database Cleanup Script: Remove Redundant Role Fields

This script removes redundant role fields from the user collection that are no longer needed
since we're using Clerk as the single source of truth for roles.

Fields to remove:
- roles (array)
- role (string) 
- organization_memberships (array)
- clerk_organizations (array)

Fields to keep:
- primary_role (synced from Clerk publicMetadata)
- organization_roles (synced from Clerk publicMetadata)
"""

import os
import sys
from pathlib import Path

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.db.mongodb import get_database
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

async def cleanup_redundant_role_fields():
    """Remove redundant role fields from user collection"""
    
    try:
        # Get database connection
        db = get_database()
        users_collection = db.users
        
        logger.info("🧹 Starting cleanup of redundant role fields...")
        
        # Find all users with redundant fields
        users_with_redundant_fields = await users_collection.find({
            "$or": [
                {"roles": {"$exists": True}},
                {"role": {"$exists": True}},
                {"organization_memberships": {"$exists": True}},
                {"clerk_organizations": {"$exists": True}}
            ]
        }).to_list(None)
        
        logger.info(f"📊 Found {len(users_with_redundant_fields)} users with redundant role fields")
        
        if not users_with_redundant_fields:
            logger.info("✅ No redundant fields found - database is already clean!")
            return
        
        # Remove redundant fields from all users
        result = await users_collection.update_many(
            {},  # Update all documents
            {
                "$unset": {
                    "roles": "",
                    "role": "",
                    "organization_memberships": "",
                    "clerk_organizations": ""
                }
            }
        )
        
        logger.info(f"✅ Successfully cleaned up {result.modified_count} user records")
        logger.info("🎯 Redundant role fields removed - Clerk is now the single source of truth!")
        
        # Verify cleanup
        remaining_redundant = await users_collection.count_documents({
            "$or": [
                {"roles": {"$exists": True}},
                {"role": {"$exists": True}},
                {"organization_memberships": {"$exists": True}},
                {"clerk_organizations": {"$exists": True}}
            ]
        })
        
        if remaining_redundant == 0:
            logger.info("✅ Verification passed - no redundant fields remain")
        else:
            logger.warning(f"⚠️ Verification failed - {remaining_redundant} documents still have redundant fields")
        
    except Exception as e:
        logger.error(f"❌ Error during cleanup: {e}")
        raise

async def main():
    """Main function"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    logger.info("🚀 Starting database cleanup for redundant role fields")
    
    try:
        await cleanup_redundant_role_fields()
        logger.info("🎉 Database cleanup completed successfully!")
        
    except Exception as e:
        logger.error(f"💥 Cleanup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())