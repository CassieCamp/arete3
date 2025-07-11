#!/usr/bin/env python3
"""
Script to find a user with 'coach' role in the MongoDB database
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
import logging
from dotenv import load_dotenv

# Load environment variables from backend/.env
load_dotenv('backend/.env')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def find_coach_user():
    """Find a user with role='coach' in the database"""
    client = None
    try:
        # Get database connection details from environment
        database_url = os.getenv('DATABASE_URL')
        database_name = os.getenv('DATABASE_NAME', 'arete_mvp')
        
        if not database_url:
            logger.error("❌ DATABASE_URL not found in environment variables")
            return None
        
        logger.info(f"Database URL: {database_url[:50]}...")
        logger.info(f"Database Name: {database_name}")
        
        # Enhanced connection options for SSL compatibility
        connection_options = {
            'tls': True,
            'tlsAllowInvalidCertificates': True,
            'tlsAllowInvalidHostnames': True,
            'serverSelectionTimeoutMS': 30000,
            'connectTimeoutMS': 30000,
            'socketTimeoutMS': 30000,
            'maxPoolSize': 10,
            'retryWrites': True,
        }
        
        logger.info("Connecting to MongoDB...")
        client = AsyncIOMotorClient(database_url, **connection_options)
        database = client[database_name]
        
        # Test the connection
        await client.admin.command('ping')
        logger.info(f"✅ Connected to MongoDB database: {database_name}")
        
        # Query for a user with role='coach'
        users_collection = database.users
        logger.info("Searching for users with role='coach'...")
        
        coach_user = await users_collection.find_one({"role": "coach"})
        
        if coach_user:
            logger.info(f"✅ Found coach user: {coach_user.get('email')}")
            print(f"Coach email: {coach_user.get('email')}")
            return coach_user.get('email')
        else:
            logger.warning("❌ No users found with role='coach'")
            
            # Let's also check what roles exist in the database
            logger.info("Checking all user roles in database...")
            all_users = await users_collection.find({}, {"email": 1, "role": 1}).to_list(length=None)
            
            if all_users:
                logger.info("All users in database:")
                for user in all_users:
                    logger.info(f"  - Email: {user.get('email')}, Role: {user.get('role')}")
            else:
                logger.info("No users found in database")
            
            return None
            
    except Exception as e:
        logger.error(f"❌ Error connecting to database or querying users: {e}")
        return None
    finally:
        if client:
            client.close()
            logger.info("Disconnected from MongoDB")

if __name__ == "__main__":
    result = asyncio.run(find_coach_user())
    if result:
        print(f"\nCOACH EMAIL FOUND: {result}")
    else:
        print("\nNo coach user found in database")