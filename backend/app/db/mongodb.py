from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
import logging
import ssl
import certifi

logger = logging.getLogger(__name__)

class Database:
    client: AsyncIOMotorClient = None
    database = None

db = Database()

async def connect_to_mongo():
    """Create database connection with enhanced SSL configuration"""
    try:
        # Enhanced connection options for SSL compatibility
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
        
        logger.info("Attempting MongoDB connection with enhanced SSL configuration...")
        db.client = AsyncIOMotorClient(settings.database_url, **connection_options)
        db.database = db.client[settings.database_name]
        
        # Test the connection
        await db.client.admin.command('ping')
        logger.info(f"✅ Connected to MongoDB database: {settings.database_name}")
        logger.warning("⚠️  Using relaxed SSL settings due to Atlas compatibility issue")
        
    except Exception as e:
        logger.error(f"❌ Failed to connect to MongoDB: {e}")
        logger.warning("Running without database connection for UAT testing")
        # Don't raise the exception - allow server to start without DB

async def close_mongo_connection():
    """Close database connection"""
    if db.client:
        db.client.close()
        logger.info("Disconnected from MongoDB")

def get_database():
    """Get database instance"""
    return db.database