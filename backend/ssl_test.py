import pymongo
import ssl
import certifi
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_ssl_connection():
    try:
        # Get connection string from environment
        connection_string = os.getenv('DATABASE_URL')
        if not connection_string:
            print("❌ DATABASE_URL not found in environment")
            return False
            
        print(f"🔍 Testing SSL connection to MongoDB Atlas...")
        print(f"SSL Version: {ssl.OPENSSL_VERSION}")
        print(f"Certifi Path: {certifi.where()}")
        
        # Test with proper SSL configuration
        client = pymongo.MongoClient(
            connection_string,
            tls=True,
            tlsCAFile=certifi.where(),
            serverSelectionTimeoutMS=10000
        )
        
        # Test the connection
        result = client.admin.command('ping')
        print('✅ SSL connection successful with proper certificate validation')
        print(f'Ping result: {result}')
        client.close()
        return True
        
    except Exception as e:
        print(f'❌ SSL connection failed: {e}')
        print(f'Error Type: {type(e).__name__}')
        return False

if __name__ == "__main__":
    test_ssl_connection()
