#!/usr/bin/env python3
"""
Script to create a hard-coded coaching relationship between specific users.

This script creates an active coaching relationship between:
- Member: user_2znorKQkuTVCyn2VNTbZAGSA6LF (cassandra310+jamie@gmail.com)
- Coach: user_2zqiKLR8NWeoMLtxm4PYxO7qeYu

Usage:
    python create_coaching_relationship.py
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.models.coaching_relationship import CoachingRelationship, RelationshipStatus
from app.repositories.coaching_relationship_repository import CoachingRelationshipRepository
from app.repositories.user_repository import UserRepository
from app.db.mongodb import get_database, connect_to_mongo, close_mongo_connection
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# User IDs
MEMBER_USER_ID = "user_2znorKQkuTVCyn2VNTbZAGSA6LF"
COACH_USER_ID = "user_2zqiKLR8NWeoMLtxm4PYxO7qeYu"

async def verify_users_exist():
    """Verify that both users exist in the database"""
    logger.info("=== Verifying users exist ===")
    
    user_repo = UserRepository()
    
    # Check member user
    member_user = await user_repo.get_user_by_clerk_id(MEMBER_USER_ID)
    if not member_user:
        logger.error(f"❌ Member user {MEMBER_USER_ID} not found in database")
        return False
    
    logger.info(f"✅ Member user found: {member_user.email} (role: {member_user.primary_role})")
    
    # Check coach user
    coach_user = await user_repo.get_user_by_clerk_id(COACH_USER_ID)
    if not coach_user:
        logger.error(f"❌ Coach user {COACH_USER_ID} not found in database")
        return False
    
    logger.info(f"✅ Coach user found: {coach_user.email} (role: {coach_user.primary_role})")
    
    return True

async def check_existing_relationship():
    """Check if a relationship already exists between these users"""
    logger.info("=== Checking for existing relationship ===")
    
    relationship_repo = CoachingRelationshipRepository()
    
    existing_relationship = await relationship_repo.get_relationship_between_users(
        COACH_USER_ID, MEMBER_USER_ID
    )
    
    if existing_relationship:
        logger.info(f"⚠️ Existing relationship found:")
        logger.info(f"   ID: {existing_relationship.id}")
        logger.info(f"   Status: {existing_relationship.status}")
        logger.info(f"   Created: {existing_relationship.created_at}")
        return existing_relationship
    
    logger.info("✅ No existing relationship found")
    return None

async def create_coaching_relationship():
    """Create a new active coaching relationship"""
    logger.info("=== Creating coaching relationship ===")
    
    relationship_repo = CoachingRelationshipRepository()
    
    # Create the relationship object
    now = datetime.utcnow()
    
    relationship = CoachingRelationship(
        # New field names
        coach_id=COACH_USER_ID,
        member_id=MEMBER_USER_ID,
        
        # Legacy field names for backward compatibility
        coach_user_id=COACH_USER_ID,
        client_user_id=MEMBER_USER_ID,
        
        # Set as active relationship
        status=RelationshipStatus.ACTIVE,
        start_date=now,
        
        # Invitation tracking
        invitation_accepted_at=now,
        
        # Timestamps
        created_at=now,
        updated_at=now
    )
    
    # Save to database
    created_relationship = await relationship_repo.create_relationship(relationship)
    
    logger.info(f"✅ Successfully created coaching relationship:")
    logger.info(f"   ID: {created_relationship.id}")
    logger.info(f"   Coach: {created_relationship.coach_user_id}")
    logger.info(f"   Member: {created_relationship.client_user_id}")
    logger.info(f"   Status: {created_relationship.status}")
    logger.info(f"   Created: {created_relationship.created_at}")
    
    return created_relationship

async def update_existing_relationship(existing_relationship):
    """Update an existing relationship to active status"""
    logger.info("=== Updating existing relationship to active ===")
    
    relationship_repo = CoachingRelationshipRepository()
    
    # Update to active status
    updated_relationship = await relationship_repo.update_relationship_status(
        str(existing_relationship.id), 
        RelationshipStatus.ACTIVE
    )
    
    if updated_relationship:
        logger.info(f"✅ Successfully updated relationship to active:")
        logger.info(f"   ID: {updated_relationship.id}")
        logger.info(f"   Status: {updated_relationship.status}")
        logger.info(f"   Updated: {updated_relationship.updated_at}")
        return updated_relationship
    else:
        logger.error("❌ Failed to update relationship status")
        return None

async def verify_relationship_creation(relationship):
    """Verify the relationship was created successfully"""
    logger.info("=== Verifying relationship creation ===")
    
    relationship_repo = CoachingRelationshipRepository()
    
    # Get active relationships for member
    member_relationships = await relationship_repo.get_active_relationships_for_user(MEMBER_USER_ID)
    logger.info(f"Member has {len(member_relationships)} active relationships")
    
    # Get active relationships for coach
    coach_relationships = await relationship_repo.get_active_relationships_for_user(COACH_USER_ID)
    logger.info(f"Coach has {len(coach_relationships)} active relationships")
    
    # Verify the specific relationship exists
    specific_relationship = await relationship_repo.get_relationship_between_users(
        COACH_USER_ID, MEMBER_USER_ID
    )
    
    if specific_relationship and specific_relationship.status == RelationshipStatus.ACTIVE:
        logger.info("✅ Relationship verification successful!")
        return True
    else:
        logger.error("❌ Relationship verification failed!")
        return False

async def main():
    """Main function to create the coaching relationship"""
    logger.info("🚀 Starting coaching relationship creation script")
    logger.info(f"Member: {MEMBER_USER_ID}")
    logger.info(f"Coach: {COACH_USER_ID}")
    
    try:
        # Initialize database connection
        logger.info("Connecting to MongoDB...")
        await connect_to_mongo()
        logger.info("✅ Connected to MongoDB")
        
        # Step 1: Verify users exist
        if not await verify_users_exist():
            logger.error("❌ User verification failed. Exiting.")
            return False
        
        # Step 2: Check for existing relationship
        existing_relationship = await check_existing_relationship()
        
        # Step 3: Create or update relationship
        if existing_relationship:
            if existing_relationship.status == RelationshipStatus.ACTIVE:
                logger.info("✅ Relationship is already active. No action needed.")
                relationship = existing_relationship
            else:
                relationship = await update_existing_relationship(existing_relationship)
                if not relationship:
                    return False
        else:
            relationship = await create_coaching_relationship()
        
        # Step 4: Verify the relationship
        if await verify_relationship_creation(relationship):
            logger.info("🎉 Coaching relationship successfully established!")
            logger.info(f"   Member {MEMBER_USER_ID} is now connected to Coach {COACH_USER_ID}")
            return True
        else:
            logger.error("❌ Relationship creation verification failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error creating coaching relationship: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False
    finally:
        # Clean up database connection
        logger.info("Disconnecting from MongoDB...")
        await close_mongo_connection()
        logger.info("✅ Disconnected from MongoDB")

if __name__ == "__main__":
    # Run the async main function
    success = asyncio.run(main())
    
    if success:
        print("\n✅ SUCCESS: Coaching relationship created successfully!")
        print("You can now test the connected coaching experience in the application.")
    else:
        print("\n❌ FAILED: Could not create coaching relationship.")
        print("Check the logs above for details.")
        sys.exit(1)