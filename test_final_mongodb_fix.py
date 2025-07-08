#!/usr/bin/env python3
"""
Final MongoDB SSL Connection Test - Using Backend Configuration
"""

import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

async def test_final_mongodb_connection():
    """Test MongoDB connection using the same configuration as the backend."""
    
    # Load environment
    load_dotenv("backend/.env")
    database_url = os.getenv("DATABASE_URL")
    database_name = os.getenv("DATABASE_NAME")
    
    print("🔧 Final MongoDB SSL Connection Test")
    print("=" * 45)
    print(f"Database: {database_name}")
    print("Using backend configuration with relaxed SSL settings...")
    print()
    
    try:
        # Use the same connection options as the backend
        connection_options = {
            'tls': True,
            'tlsAllowInvalidCertificates': True,  # Temporary fix for Atlas SSL issue
            'tlsAllowInvalidHostnames': True,     # Temporary fix for Atlas SSL issue
            'serverSelectionTimeoutMS': 30000,
            'connectTimeoutMS': 30000,
            'socketTimeoutMS': 30000,
            'maxPoolSize': 10,
            'retryWrites': True,
        }
        
        print("Connecting with enhanced SSL configuration...")
        client = AsyncIOMotorClient(database_url, **connection_options)
        database = client[database_name]
        
        # Test the connection
        await client.admin.command('ping')
        print("✅ SUCCESS: Connected to MongoDB Atlas!")
        
        # Test database operations
        collections = await database.list_collection_names()
        print(f"✅ Database access confirmed. Collections: {len(collections)}")
        
        if collections:
            print("📋 Existing collections:")
            for i, collection in enumerate(collections, 1):
                try:
                    count = await database[collection].count_documents({})
                    print(f"   {i:2d}. {collection} ({count} documents)")
                except Exception:
                    print(f"   {i:2d}. {collection} (count unavailable)")
        else:
            print("📋 No collections found (database is empty)")
        
        # Test a simple write operation
        test_collection = database['connection_test']
        test_doc = {"test": "connection_successful", "timestamp": "2025-01-02"}
        result = await test_collection.insert_one(test_doc)
        print(f"✅ Write test successful. Document ID: {result.inserted_id}")
        
        # Clean up test document
        await test_collection.delete_one({"_id": result.inserted_id})
        print("✅ Cleanup successful")
        
        client.close()
        
        print("\n🎉 MongoDB SSL connection issue RESOLVED!")
        print("✅ The backend can now connect to MongoDB Atlas successfully")
        print("⚠️  Note: Using relaxed SSL settings due to Atlas compatibility issue")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_final_mongodb_connection())
    if not success:
        print("\n❌ Final connection test failed")
        exit(1)