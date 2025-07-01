#!/usr/bin/env python3
"""
Direct script to restore the connection between coach and client accounts
This bypasses the API and works directly with the database
"""
import asyncio
import sys
import os
from datetime import datetime

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Set environment variables
os.environ['DATABASE_URL'] = 'mongodb://localhost:27017/'
os.environ['DATABASE_NAME'] = 'arete_mvp_test'
os.environ['CLERK_SECRET_KEY'] = 'sk_test_lmSNNAI1wCJjoON8EYab6kv0SGg9FdGSp0WLtDlMvI'
os.environ['CLERK_WEBHOOK_SECRET'] = 'whsec_placeholder_for_development'

from app.models.coaching_relationship import CoachingRelationship, RelationshipStatus
from app.repositories.coaching_relationship_repository import CoachingRelationshipRepository
from app.repositories.user_repository import UserRepository

async def restore_connection():
    """Restore the connection between coach and client"""
    print("=== Restoring Coach-Client Connection ===")
    
    try:
        # Initialize repositories
        relationship_repo = CoachingRelationshipRepository()
        user_repo = UserRepository()
        
        # User details
        coach_email = "cassandra310+coach@gmail.com"
        client_email = "cassandra310+client8@gmail.com"
        
        print(f"Coach Email: {coach_email}")
        print(f"Client Email: {client_email}")
        
        # Get the users
        coach_user = await user_repo.get_user_by_email(coach_email)
        client_user = await user_repo.get_user_by_email(client_email)
        
        if not coach_user:
            print(f"❌ Coach not found: {coach_email}")
            return
        
        if not client_user:
            print(f"❌ Client not found: {client_email}")
            return
        
        print(f"✅ Found coach: {coach_user.clerk_user_id} ({coach_user.email})")
        print(f"✅ Found client: {client_user.clerk_user_id} ({client_user.email})")
        
        # Check if a relationship already exists
        existing_rel = await relationship_repo.get_relationship_between_users(
            coach_user.clerk_user_id, client_user.clerk_user_id
        )
        
        if existing_rel:
            print(f"⚠️ Relationship already exists: {existing_rel.id} (status: {existing_rel.status})")
            
            if existing_rel.status == RelationshipStatus.ACTIVE:
                print("✅ Connection is already active!")
                return
            elif existing_rel.status == RelationshipStatus.PENDING_BY_COACH:
                print("🔄 Activating existing pending relationship...")
                updated_rel = await relationship_repo.update_relationship_status(
                    str(existing_rel.id), RelationshipStatus.ACTIVE
                )
                if updated_rel:
                    print("✅ Successfully activated existing relationship!")
                    return
                else:
                    print("❌ Failed to activate existing relationship")
                    return
        
        # Create new relationship
        print("🔄 Creating new coaching relationship...")
        
        new_relationship = CoachingRelationship(
            coach_user_id=coach_user.clerk_user_id,
            client_user_id=client_user.clerk_user_id,
            status=RelationshipStatus.ACTIVE,  # Create it as active directly
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        created_rel = await relationship_repo.create_relationship(new_relationship)
        
        if created_rel:
            print(f"✅ Successfully created active coaching relationship!")
            print(f"Relationship ID: {created_rel.id}")
            print(f"Status: {created_rel.status}")
            print("🎉 Connection restored!")
        else:
            print("❌ Failed to create relationship")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(restore_connection())