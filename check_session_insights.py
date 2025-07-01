#!/usr/bin/env python3

import os
import sys
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def check_session_insights():
    # Connect to MongoDB
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    client = AsyncIOMotorClient(mongodb_url)
    db = client["arete_coaching"]
    
    # Check for any session insights for the client user
    client_user_id = 'user_2zEbicg7TUWFHOT7rQQm1DEODjP'
    coach_user_id = 'user_2z8yf2QwU5mvpGWFlwNkegdxi2m'
    new_relationship_id = '686331d8ba9d494a58b8edf6'
    
    print('=== Checking session_insights collection ===')
    insights_collection = db['session_insights']
    
    # Find insights by client_user_id
    client_insights = []
    async for insight in insights_collection.find({'client_user_id': client_user_id}):
        client_insights.append(insight)
    
    print(f'Found {len(client_insights)} insights for client {client_user_id}')
    
    for insight in client_insights:
        print(f'  - Insight ID: {insight["_id"]}')
        print(f'    Relationship ID: {insight.get("coaching_relationship_id", "N/A")}')
        print(f'    Session Title: {insight.get("session_title", "N/A")}')
        print(f'    Created: {insight.get("created_at", "N/A")}')
        print(f'    Status: {insight.get("status", "N/A")}')
        print()
    
    # Also check by coach_user_id
    coach_insights = []
    async for insight in insights_collection.find({'coach_user_id': coach_user_id}):
        coach_insights.append(insight)
    
    print(f'Found {len(coach_insights)} insights for coach {coach_user_id}')
    
    for insight in coach_insights:
        print(f'  - Insight ID: {insight["_id"]}')
        print(f'    Relationship ID: {insight.get("coaching_relationship_id", "N/A")}')
        print(f'    Session Title: {insight.get("session_title", "N/A")}')
        print(f'    Created: {insight.get("created_at", "N/A")}')
        print(f'    Status: {insight.get("status", "N/A")}')
        print()
    
    # Check total count in collection
    total_insights = await insights_collection.count_documents({})
    print(f'Total insights in collection: {total_insights}')
    
    # If we found orphaned insights, offer to update them
    orphaned_insights = []
    for insight in client_insights + coach_insights:
        if insight.get('coaching_relationship_id') != new_relationship_id:
            orphaned_insights.append(insight)
    
    if orphaned_insights:
        print(f'\n=== Found {len(orphaned_insights)} potentially orphaned insights ===')
        print('These insights may need to be updated to reference the new relationship ID.')
        
        for insight in orphaned_insights:
            print(f'  - {insight["_id"]}: {insight.get("session_title", "Untitled")} (Relationship: {insight.get("coaching_relationship_id", "N/A")})')
        
        print(f'\nTo restore these insights, they should be updated to reference relationship ID: {new_relationship_id}')
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check_session_insights())