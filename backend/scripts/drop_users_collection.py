import asyncio
import logging
from app.db.mongodb import get_database, close_mongo_connection

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from app.db.mongodb import connect_to_mongo, get_database, close_mongo_connection

async def drop_users_collection():
    """
    Drops the `users` collection from the MongoDB database.
    """
    db = None
    try:
        await connect_to_mongo()
        db = get_database()
        logger.info("Attempting to drop the 'users' collection...")
        
        # Check if the collection exists before dropping
        collection_names = await db.list_collection_names()
        if "users" in collection_names:
            await db.drop_collection("users")
            logger.info("✅ Successfully dropped the 'users' collection.")
        else:
            logger.info("✅ The 'users' collection does not exist, no action needed.")

    except Exception as e:
        logger.error(f"❌ Failed to drop the 'users' collection. Error: {e}")
    finally:
        if db is not None:
            await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(drop_users_collection())