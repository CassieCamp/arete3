#!/usr/bin/env python3
"""
Script to clean up all data for a specific user from journey collections.

This script removes:
- All reflection records for the user from journey_reflections collection
- All insight records for the user from journey_insights collection
"""

import asyncio
import sys
import os
import logging

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.db.mongodb import connect_to_mongo, close_mongo_connection, get_database
from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def cleanup_user_data(user_id: str):
    """
    Clean up all journey data for a specific user.
    
    Args:
        user_id (str): The Clerk user ID to clean up
        
    Returns:
        dict: Summary of the cleanup operation
    """
    try:
        # Connect to MongoDB
        logger.info("Connecting to MongoDB...")
        await connect_to_mongo()
        
        db = get_database()
        if db is None:
            logger.error("Failed to get database connection")
            return None
        
        logger.info(f"Connected to database: {settings.database_name}")
        logger.info(f"Cleaning up data for user: {user_id}")
        
        # Target collections and their user field
        target_collections = [
            ('journey_reflections', 'user_id'),
            ('journey_insights', 'user_id')
        ]
        
        results = {}
        total_deleted = 0
        
        for collection_name, user_field in target_collections:
            logger.info(f"Processing collection: {collection_name}")
            
            collection = db[collection_name]
            
            # Count documents before deletion
            query = {user_field: user_id}
            doc_count_before = await collection.count_documents(query)
            logger.info(f"Found {doc_count_before} documents for user {user_id} in {collection_name}")
            
            if doc_count_before > 0:
                # Delete user's documents
                delete_result = await collection.delete_many(query)
                deleted_count = delete_result.deleted_count
                
                # Verify deletion
                doc_count_after = await collection.count_documents(query)
                
                if doc_count_after == 0:
                    logger.info(f"✅ Successfully deleted {deleted_count} documents from {collection_name}")
                    results[collection_name] = {
                        'documents_before': doc_count_before,
                        'documents_deleted': deleted_count,
                        'documents_after': doc_count_after,
                        'status': 'success'
                    }
                else:
                    logger.warning(f"⚠️  Partial deletion in {collection_name}: {doc_count_after} documents remain")
                    results[collection_name] = {
                        'documents_before': doc_count_before,
                        'documents_deleted': deleted_count,
                        'documents_after': doc_count_after,
                        'status': 'partial'
                    }
                
                total_deleted += deleted_count
            else:
                logger.info(f"No documents found for user {user_id} in {collection_name}")
                results[collection_name] = {
                    'documents_before': 0,
                    'documents_deleted': 0,
                    'documents_after': 0,
                    'status': 'no_data'
                }
        
        results['total_deleted'] = total_deleted
        return results
        
    except Exception as e:
        logger.error(f"❌ Error during user data cleanup: {e}")
        return None
    
    finally:
        # Close database connection
        await close_mongo_connection()
        logger.info("Database connection closed")

def print_summary(user_id: str, results):
    """
    Print a formatted summary of the cleanup operation.
    
    Args:
        user_id (str): The user ID that was cleaned up
        results (dict): Results from the cleanup operation
    """
    if not results:
        print("\n❌ OPERATION FAILED")
        print("Unable to clean up user data due to errors.")
        return
    
    print("\n" + "="*60)
    print(f"USER DATA CLEANUP SUMMARY")
    print(f"User ID: {user_id}")
    print("="*60)
    
    total_deleted = results.get('total_deleted', 0)
    
    for collection_name, result in results.items():
        if collection_name == 'total_deleted':
            continue
            
        status_icon = {
            'success': '✅',
            'partial': '⚠️',
            'no_data': 'ℹ️'
        }.get(result['status'], '❓')
        
        print(f"\n{status_icon} Collection: {collection_name}")
        print(f"   Documents before: {result['documents_before']}")
        print(f"   Documents deleted: {result['documents_deleted']}")
        print(f"   Documents after: {result['documents_after']}")
        print(f"   Status: {result['status'].replace('_', ' ').title()}")
    
    print(f"\n📊 TOTAL DOCUMENTS DELETED: {total_deleted}")
    print("="*60)
    
    if total_deleted > 0:
        print(f"\n✅ Successfully cleaned up all data for user {user_id}")
    else:
        print(f"\nℹ️  No data found for user {user_id}")

async def main():
    """
    Main function to execute the user cleanup operation.
    """
    # Target user ID
    user_id = "user_2zvLlq0XW9KcLM2ocSozcPSO60p"
    
    print("🧹 User Data Cleanup Script")
    print("="*40)
    print(f"Target User ID: {user_id}")
    print("This script will clean up ALL documents for this user from:")
    print("- journey_reflections collection")
    print("- journey_insights collection")
    
    print(f"\nStarting cleanup operation for user {user_id}...")
    
    # Execute the cleanup operation
    results = await cleanup_user_data(user_id)
    
    # Print summary
    print_summary(user_id, results)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nOperation interrupted by user.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)