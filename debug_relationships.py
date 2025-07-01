#!/usr/bin/env python3
"""
Debug script to check coaching relationships in the database
"""
import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.db.mongodb import get_database
from app.repositories.coaching_relationship_repository import CoachingRelationshipRepository
from app.repositories.user_repository import UserRepository

async def debug_relationships():
    """Debug coaching relationships"""
    print("=== Debugging Coaching Relationships ===")
    
    try:
        # Get database connection
        db = get_database()
        if db is None:
            print("❌ Could not connect to database")
            return
        
        print("✅ Connected to database")
        
        # Initialize repositories
        relationship_repo = CoachingRelationshipRepository()
        user_repo = UserRepository()
        
        # Get the specific users
        coach_email = "cassandra310+coach@gmail.com"
        client_email = "cassandra310+client8@gmail.com"
        
        print(f"\n=== Looking for users ===")
        coach_user = await user_repo.get_user_by_email(coach_email)
        client_user = await user_repo.get_user_by_email(client_email)
        
        if coach_user:
            print(f"✅ Found coach: {coach_user.clerk_user_id} ({coach_user.email})")
        else:
            print(f"❌ Coach not found: {coach_email}")
            
        if client_user:
            print(f"✅ Found client: {client_user.clerk_user_id} ({client_user.email})")
        else:
            print(f"❌ Client not found: {client_email}")
        
        if not coach_user or not client_user:
            print("Cannot proceed without both users")
            return
        
        # Check for any relationships in the database
        print(f"\n=== Checking all coaching relationships ===")
        collection = db["coaching_relationships"]
        all_relationships = await collection.find({}).to_list(length=None)
        
        print(f"Total relationships in database: {len(all_relationships)}")
        
        for rel in all_relationships:
            print(f"Relationship: {rel}")
        
        # Check for specific relationship between these users
        print(f"\n=== Checking specific relationship ===")
        specific_rel = await relationship_repo.get_relationship_between_users(
            coach_user.clerk_user_id, client_user.clerk_user_id
        )
        
        if specific_rel:
            print(f"✅ Found relationship: {specific_rel}")
        else:
            print("❌ No relationship found between these specific users")
        
        # Check relationships for each user
        print(f"\n=== Checking coach relationships ===")
        coach_relationships = await relationship_repo.get_user_relationships(coach_user.clerk_user_id)
        print(f"Coach pending: {len(coach_relationships.get('pending', []))}")
        print(f"Coach active: {len(coach_relationships.get('active', []))}")
        
        print(f"\n=== Checking client relationships ===")
        client_relationships = await relationship_repo.get_user_relationships(client_user.clerk_user_id)
        print(f"Client pending: {len(client_relationships.get('pending', []))}")
        print(f"Client active: {len(client_relationships.get('active', []))}")
        
        # Check for any relationships involving these users with any status
        print(f"\n=== Checking for any relationships involving these users ===")
        coach_any = await collection.find({
            "$or": [
                {"coach_user_id": coach_user.clerk_user_id},
                {"client_user_id": coach_user.clerk_user_id}
            ]
        }).to_list(length=None)
        
        client_any = await collection.find({
            "$or": [
                {"coach_user_id": client_user.clerk_user_id},
                {"client_user_id": client_user.clerk_user_id}
            ]
        }).to_list(length=None)
        
        print(f"Coach involved in {len(coach_any)} relationships:")
        for rel in coach_any:
            print(f"  - {rel}")
            
        print(f"Client involved in {len(client_any)} relationships:")
        for rel in client_any:
            print(f"  - {rel}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_relationships())