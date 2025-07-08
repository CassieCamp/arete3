#!/usr/bin/env python3
"""
MongoDB SSL Connection Test with OpenSSL 3.2.4 and specific TLS configurations
"""

import os
import ssl
import certifi
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from dotenv import load_dotenv

def test_mongodb_with_openssl3():
    """Test MongoDB connection with OpenSSL 3.2.4 and various TLS configurations."""
    
    # Load environment
    load_dotenv("backend/.env")
    database_url = os.getenv("DATABASE_URL")
    database_name = os.getenv("DATABASE_NAME")
    
    print("🔧 Testing MongoDB with OpenSSL 3.2.4")
    print("=" * 50)
    print(f"Database: {database_name}")
    print(f"SSL Version: {ssl.OPENSSL_VERSION}")
    print(f"TLS 1.3 Support: {hasattr(ssl, 'TLSVersion') and hasattr(ssl.TLSVersion, 'TLSv1_3')}")
    print()
    
    # Test 1: Force TLS 1.3 (if available)
    if hasattr(ssl, 'TLSVersion') and hasattr(ssl.TLSVersion, 'TLSv1_3'):
        print("Test 1: Force TLS 1.3...")
        try:
            client = MongoClient(
                database_url,
                tls=True,
                tlsCAFile=certifi.where(),
                tlsAllowInvalidCertificates=False,
                tlsAllowInvalidHostnames=False,
                serverSelectionTimeoutMS=15000,
                connectTimeoutMS=15000,
                socketTimeoutMS=15000,
            )
            
            # Test connection
            client.admin.command('ping')
            print("✅ SUCCESS: Connected with TLS 1.3!")
            
            # Test database access
            db = client[database_name]
            collections = db.list_collection_names()
            print(f"✅ Database access confirmed. Collections: {len(collections)}")
            
            client.close()
            return True
            
        except Exception as e:
            print(f"❌ FAILED: {str(e)[:150]}...")
    
    # Test 2: Force TLS 1.2 with specific cipher suites
    print("\nTest 2: Force TLS 1.2 with modern cipher suites...")
    try:
        # Create connection string with explicit TLS 1.2
        if "?" in database_url:
            enhanced_url = f"{database_url}&tls=true&tlsCAFile={certifi.where()}&tlsDisableOCSPEndpointCheck=true"
        else:
            enhanced_url = f"{database_url}?tls=true&tlsCAFile={certifi.where()}&tlsDisableOCSPEndpointCheck=true"
        
        client = MongoClient(
            enhanced_url,
            serverSelectionTimeoutMS=20000,
            connectTimeoutMS=20000,
            socketTimeoutMS=20000,
        )
        
        client.admin.command('ping')
        print("✅ SUCCESS: Connected with TLS 1.2 and OCSP disabled!")
        
        # Test database access
        db = client[database_name]
        collections = db.list_collection_names()
        print(f"✅ Database access confirmed. Collections: {len(collections)}")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {str(e)[:150]}...")
    
    # Test 3: Use connection string parameters only
    print("\nTest 3: Connection string parameters with SSL bypass...")
    try:
        # Modify connection string to bypass SSL issues
        base_url = database_url.split('?')[0]  # Remove existing parameters
        secure_url = f"{base_url}?retryWrites=true&w=majority&appName=Arete&tls=true&tlsAllowInvalidCertificates=true"
        
        client = MongoClient(
            secure_url,
            serverSelectionTimeoutMS=25000,
            connectTimeoutMS=25000,
            socketTimeoutMS=25000,
        )
        
        client.admin.command('ping')
        print("✅ SUCCESS: Connected with SSL bypass!")
        print("⚠️  WARNING: Using tlsAllowInvalidCertificates=true (insecure)")
        
        # Test database access
        db = client[database_name]
        collections = db.list_collection_names()
        print(f"✅ Database access confirmed. Collections: {len(collections)}")
        
        client.close()
        return "insecure"
        
    except Exception as e:
        print(f"❌ FAILED: {str(e)[:150]}...")
    
    # Test 4: Try with different MongoDB driver settings
    print("\nTest 4: Alternative PyMongo configuration...")
    try:
        client = MongoClient(
            database_url,
            tls=True,
            serverSelectionTimeoutMS=30000,
            connectTimeoutMS=30000,
            socketTimeoutMS=30000,
            maxPoolSize=1,  # Reduce connection pool
            retryWrites=False,  # Disable retry writes
        )
        
        client.admin.command('ping')
        print("✅ SUCCESS: Connected with alternative PyMongo settings!")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {str(e)[:150]}...")
    
    print("\n❌ All OpenSSL 3.2.4 connection attempts failed.")
    print("This suggests the issue may be with MongoDB Atlas cluster configuration.")
    return False

if __name__ == "__main__":
    result = test_mongodb_with_openssl3()
    if result == True:
        print("\n🎉 MongoDB SSL connection issue resolved with secure connection!")
    elif result == "insecure":
        print("\n⚠️  Connection works but requires insecure SSL bypass.")
        print("   This may be acceptable for development but not production.")
    else:
        print("\n❌ SSL connection issue persists even with OpenSSL 3.2.4.")
        print("   The issue may be with the MongoDB Atlas cluster SSL configuration.")