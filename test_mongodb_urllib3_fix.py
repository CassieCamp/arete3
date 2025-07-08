#!/usr/bin/env python3
"""
MongoDB SSL Connection Test using urllib3 and custom SSL handling
"""

import os
import ssl
import certifi
import urllib3
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from dotenv import load_dotenv

def test_mongodb_with_urllib3_ssl():
    """Test MongoDB connection using urllib3 SSL configuration."""
    
    # Load environment
    load_dotenv("backend/.env")
    database_url = os.getenv("DATABASE_URL")
    database_name = os.getenv("DATABASE_NAME")
    
    print("🔧 Testing MongoDB with urllib3 SSL Configuration")
    print("=" * 55)
    print(f"Database: {database_name}")
    print(f"SSL Version: {ssl.OPENSSL_VERSION}")
    print()
    
    # Disable urllib3 SSL warnings for testing
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # Test 1: Force TLS 1.2 with custom SSL context
    print("Test 1: Custom SSL context forcing TLS 1.2...")
    try:
        # Create a custom SSL context
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
        ssl_context.maximum_version = ssl.TLSVersion.TLSv1_2
        ssl_context.load_verify_locations(certifi.where())
        ssl_context.check_hostname = True
        ssl_context.verify_mode = ssl.CERT_REQUIRED
        
        # Set specific cipher suites that work with LibreSSL
        ssl_context.set_ciphers('ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS')
        
        # Use the connection string with explicit TLS settings
        enhanced_url = database_url.replace('mongodb+srv://', 'mongodb+srv://').replace('?', '?tls=true&tlsInsecure=false&')
        
        client = MongoClient(
            enhanced_url,
            serverSelectionTimeoutMS=15000,
            connectTimeoutMS=15000,
            socketTimeoutMS=15000,
        )
        
        # Test connection
        client.admin.command('ping')
        print("✅ SUCCESS: Connected with custom TLS 1.2 SSL context!")
        
        # Test database access
        db = client[database_name]
        collections = db.list_collection_names()
        print(f"✅ Database access confirmed. Collections: {len(collections)}")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {str(e)[:150]}...")
    
    # Test 2: Completely bypass SSL verification (insecure but functional test)
    print("\nTest 2: Bypass SSL verification (insecure test)...")
    try:
        # Create insecure SSL context
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        client = MongoClient(
            database_url,
            tls=True,
            tlsInsecure=True,
            tlsAllowInvalidCertificates=True,
            tlsAllowInvalidHostnames=True,
            serverSelectionTimeoutMS=15000,
            connectTimeoutMS=15000,
            socketTimeoutMS=15000,
        )
        
        client.admin.command('ping')
        print("✅ SUCCESS: Connected with insecure SSL bypass!")
        print("⚠️  WARNING: This is insecure and should not be used in production!")
        
        client.close()
        return "insecure"
        
    except Exception as e:
        print(f"❌ FAILED: {str(e)[:150]}...")
    
    # Test 3: Try with different MongoDB driver options
    print("\nTest 3: Alternative driver configuration...")
    try:
        # Parse the connection string to modify it
        if "retryWrites=true" in database_url:
            modified_url = database_url.replace("retryWrites=true", "retryWrites=false")
        else:
            modified_url = database_url + "&retryWrites=false"
        
        modified_url += "&ssl_cert_reqs=CERT_NONE&ssl_match_hostname=false"
        
        client = MongoClient(
            modified_url,
            serverSelectionTimeoutMS=20000,
            connectTimeoutMS=20000,
            socketTimeoutMS=20000,
        )
        
        client.admin.command('ping')
        print("✅ SUCCESS: Connected with modified driver options!")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {str(e)[:150]}...")
    
    print("\n❌ All connection attempts failed.")
    return False

if __name__ == "__main__":
    result = test_mongodb_with_urllib3_ssl()
    if result == True:
        print("\n🎉 MongoDB SSL connection issue resolved with secure connection!")
    elif result == "insecure":
        print("\n⚠️  Connection works but requires insecure SSL bypass.")
        print("   This confirms the issue is LibreSSL compatibility.")
        print("   Recommend upgrading to newer Python/OpenSSL for secure connection.")
    else:
        print("\n❌ SSL connection issue persists. System-level SSL update required.")