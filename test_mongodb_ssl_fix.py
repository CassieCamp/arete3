#!/usr/bin/env python3
"""
MongoDB SSL Connection Test with Enhanced SSL Configuration
"""

import os
import ssl
import certifi
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from dotenv import load_dotenv

def test_mongodb_connection():
    """Test MongoDB connection with various SSL configurations."""
    
    # Load environment
    load_dotenv("backend/.env")
    database_url = os.getenv("DATABASE_URL")
    database_name = os.getenv("DATABASE_NAME")
    
    print("🔧 Testing MongoDB SSL Connection Fixes")
    print("=" * 50)
    print(f"Database: {database_name}")
    print(f"SSL Version: {ssl.OPENSSL_VERSION}")
    print(f"Certifi Version: {certifi.__version__}")
    print(f"Certifi CA Bundle: {certifi.where()}")
    print()
    
    # Test 1: Use certifi CA bundle with modern PyMongo TLS parameters
    print("Test 1: Using certifi CA bundle with TLS parameters...")
    try:
        client = MongoClient(
            database_url,
            tls=True,
            tlsCAFile=certifi.where(),
            tlsAllowInvalidCertificates=False,
            tlsAllowInvalidHostnames=False,
            serverSelectionTimeoutMS=10000,
            connectTimeoutMS=10000,
            socketTimeoutMS=10000,
        )
        
        # Test connection
        client.admin.command('ping')
        print("✅ SUCCESS: Connected with certifi CA bundle!")
        
        # Test database access
        db = client[database_name]
        collections = db.list_collection_names()
        print(f"✅ Database access confirmed. Collections: {len(collections)}")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {str(e)[:100]}...")
    
    # Test 2: Relaxed TLS with certifi
    print("\nTest 2: Relaxed TLS with certifi CA bundle...")
    try:
        client = MongoClient(
            database_url,
            tls=True,
            tlsCAFile=certifi.where(),
            tlsAllowInvalidCertificates=True,
            tlsAllowInvalidHostnames=True,
            serverSelectionTimeoutMS=10000,
            connectTimeoutMS=10000,
            socketTimeoutMS=10000,
        )
        
        client.admin.command('ping')
        print("✅ SUCCESS: Connected with relaxed TLS!")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {str(e)[:100]}...")
    
    # Test 3: Connection string parameters
    print("\nTest 3: Using connection string SSL parameters...")
    try:
        # Add SSL parameters to connection string
        if "?" in database_url:
            enhanced_url = f"{database_url}&tls=true&tlsCAFile={certifi.where()}&tlsAllowInvalidHostnames=false"
        else:
            enhanced_url = f"{database_url}?tls=true&tlsCAFile={certifi.where()}&tlsAllowInvalidHostnames=false"
        
        client = MongoClient(
            enhanced_url,
            serverSelectionTimeoutMS=10000,
            connectTimeoutMS=10000,
            socketTimeoutMS=10000,
        )
        
        client.admin.command('ping')
        print("✅ SUCCESS: Connected with enhanced connection string!")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {str(e)[:100]}...")
    
    print("\n❌ All SSL connection tests failed.")
    return False

if __name__ == "__main__":
    success = test_mongodb_connection()
    if success:
        print("\n🎉 MongoDB SSL connection issue resolved!")
    else:
        print("\n⚠️  SSL connection issue persists. May need system-level SSL update.")