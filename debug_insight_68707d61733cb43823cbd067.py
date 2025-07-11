#!/usr/bin/env python3

import os
import sys
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

async def debug_specific_insight():
    # Connect to MongoDB using the correct connection string from .env
    mongodb_url = "mongodb+srv://cassie:mSt2YiY^hjgX@arete.6cwmnzs.mongodb.net/?retryWrites=true&w=majority&appName=Arete"
    client = AsyncIOMotorClient(mongodb_url)
    db = client["arete_mvp"]  # Correct database name
    
    insight_id = "68707d61733cb43823cbd067"
    
    print(f'=== Debugging insight {insight_id} ===')
    
    # Check in entries collection (where repository looks)
    print('\n--- Checking entries collection ---')
    entries_collection = db['entries']
    
    try:
        doc = await entries_collection.find_one({'_id': ObjectId(insight_id)})
        if doc:
            print('✅ FOUND IN ENTRIES COLLECTION')
            print(f'Document keys: {list(doc.keys())}')
            print('\nDocument structure:')
            for key, value in doc.items():
                if key == '_id':
                    print(f'  {key}: {value}')
                elif isinstance(value, dict):
                    print(f'  {key}: dict with keys {list(value.keys())}')
                elif isinstance(value, list):
                    print(f'  {key}: list with {len(value)} items')
                    if value and isinstance(value[0], dict):
                        print(f'    First item keys: {list(value[0].keys())}')
                else:
                    print(f'  {key}: {type(value).__name__} = {value}')
                    
            # Check for missing required fields from SessionInsight model
            required_fields = [
                'client_user_id', 'transcript_source', 'session_summary', 
                'overall_session_quality', 'status', 'created_by', 'created_at', 'updated_at'
            ]
            
            print('\n--- Required Field Analysis ---')
            missing_fields = []
            for field in required_fields:
                if field not in doc:
                    missing_fields.append(field)
                    print(f'❌ MISSING: {field}')
                else:
                    print(f'✅ PRESENT: {field} = {doc[field]}')
            
            if missing_fields:
                print(f'\n🚨 VALIDATION ISSUE: {len(missing_fields)} required fields are missing!')
                print(f'Missing fields: {missing_fields}')
            else:
                print('\n✅ All required fields are present')
                
        else:
            print('❌ NOT FOUND IN ENTRIES COLLECTION')
    except Exception as e:
        print(f'❌ Error checking entries collection: {e}')
    
    # Check in old session_insights collection
    print('\n--- Checking session_insights collection ---')
    session_insights_collection = db['session_insights']
    
    try:
        old_doc = await session_insights_collection.find_one({'_id': ObjectId(insight_id)})
        if old_doc:
            print('✅ FOUND IN OLD SESSION_INSIGHTS COLLECTION')
            print(f'Document keys: {list(old_doc.keys())}')
            print('\nThis suggests the migration may not have completed properly')
        else:
            print('❌ NOT FOUND IN SESSION_INSIGHTS COLLECTION')
    except Exception as e:
        print(f'❌ Error checking session_insights collection: {e}')
    
    # List all collections to see what exists
    print('\n--- Available Collections ---')
    collections = await db.list_collection_names()
    for collection in sorted(collections):
        count = await db[collection].count_documents({})
        print(f'  {collection}: {count} documents')
    
    client.close()

if __name__ == "__main__":
    asyncio.run(debug_specific_insight())