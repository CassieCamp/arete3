#!/usr/bin/env python3
"""
Quick script to check what's in the MongoDB database
"""
import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.db.mongodb import connect_to_mongo, get_database
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def check_database():
    """Check what collections and documents exist in the database"""
    try:
        # Connect to database
        await connect_to_mongo()
        db = get_database()
        
        if db is None:
            print("❌ Could not connect to database")
            return
        
        print("✅ Connected to MongoDB database")
        
        # List all collections
        collections = await db.list_collection_names()
        print(f"\n📁 Collections in database: {collections}")
        
        # Check specific collections we're interested in
        collections_to_check = [
            "journey_insights",
            "journey_reflections", 
            "reflections",
            "insights",
            "documents",
            "uploads"
        ]
        
        for collection_name in collections_to_check:
            if collection_name in collections:
                count = await db[collection_name].count_documents({})
                print(f"\n📊 Collection '{collection_name}': {count} documents")
                
                if count > 0:
                    # Show first few documents
                    cursor = db[collection_name].find({}).limit(3)
                    docs = await cursor.to_list(length=3)
                    print(f"   Sample documents:")
                    for i, doc in enumerate(docs, 1):
                        # Remove _id for cleaner output
                        doc_copy = dict(doc)
                        if '_id' in doc_copy:
                            doc_copy['_id'] = str(doc_copy['_id'])
                        print(f"   {i}. {doc_copy}")
            else:
                print(f"\n📊 Collection '{collection_name}': Not found")
        
        # Check uploads directory
        uploads_dir = "backend/uploads"
        if os.path.exists(uploads_dir):
            files = os.listdir(uploads_dir)
            print(f"\n📁 Files in uploads directory: {len(files)}")
            for file in files[:5]:  # Show first 5 files
                print(f"   - {file}")
        else:
            print(f"\n📁 Uploads directory '{uploads_dir}' does not exist")
            
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_database())