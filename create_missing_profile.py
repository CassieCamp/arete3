#!/usr/bin/env python3
"""
Script to create missing profile for existing user
"""
import asyncio
import sys
import os
from datetime import datetime

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.db.mongodb import connect_to_mongo, close_mongo_connection
from app.repositories.user_repository import UserRepository
from app.repositories.profile_repository import ProfileRepository
from app.models.profile import Profile, FreemiumStatus, DashboardPreferences, RedesignFeatures


async def create_missing_profile():
    """Create missing profile for the existing user"""
    try:
        # Connect to database
        await connect_to_mongo()
        print("✅ Connected to MongoDB")
        
        # Initialize repositories
        user_repo = UserRepository()
        profile_repo = ProfileRepository()
        
        # Get the existing user
        clerk_user_id = "user_2zACkDouPZ9GWRgDdsdpwcUy6aY"
        user = await user_repo.get_user_by_clerk_id(clerk_user_id)
        
        if not user:
            print(f"❌ User with clerk_id {clerk_user_id} not found")
            return
            
        print(f"✅ Found user: {user.email} (role: {user.role})")
        
        # Check if profile already exists
        existing_profile = await profile_repo.get_profile_by_clerk_id(clerk_user_id)
        if existing_profile:
            print(f"✅ Profile already exists for user {clerk_user_id}")
            return
            
        # Create new profile
        profile = Profile(
            user_id=str(user.id),
            clerk_user_id=clerk_user_id,
            first_name="Cassandra",  # From email cassandra310+client1@gmail.com
            last_name="Client",
            freemium_status=FreemiumStatus(
                has_coach=False,
                entries_count=0,
                max_free_entries=3,
                coach_requested=False
            ),
            dashboard_preferences=DashboardPreferences(
                preferred_landing_tab="journey",
                onboarding_completed=False,
                tooltips_shown=False
            ),
            redesign_features=RedesignFeatures(
                unified_entries=True,
                destinations_rebrand=True,
                mountain_navigation=True,
                freemium_gating=True
            ),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Save profile
        created_profile = await profile_repo.create_profile(profile)
        print(f"✅ Created profile with ID: {created_profile.id}")
        print(f"   - Name: {created_profile.first_name} {created_profile.last_name}")
        print(f"   - Clerk ID: {created_profile.clerk_user_id}")
        print(f"   - Freemium status: {created_profile.freemium_status}")
        
    except Exception as e:
        print(f"❌ Error creating profile: {e}")
        raise
    finally:
        await close_mongo_connection()
        print("✅ Disconnected from MongoDB")


if __name__ == "__main__":
    asyncio.run(create_missing_profile())