#!/usr/bin/env python3
"""
Script to clear all documents from journey_reflections and journey_insights collections.

This script connects to MongoDB using the existing database connection logic
and safely clears the specified collections while providing detailed feedback.
"""

import asyncio
import sys
import os
import logging

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.db.mongodb import connect_to_mongo, close_mongo_connection, get_database
from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def clear_journey_collections():
    """
    Clear all documents from journey_reflections and journey_insights collections.
    
    Returns:
        dict: Summary of the clearing operation with collection names and document counts
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
        
        # Target collections
        target_collections = ['journey_reflections', 'journey_insights']
        results = {}
        
        for collection_name in target_collections:
            logger.info(f"Processing collection: {collection_name}")
            
            collection = db[collection_name]
            
            # Count documents before deletion
            doc_count_before = await collection.count_documents({})
            logger.info(f"Found {doc_count_before} documents in {collection_name}")
            
            if doc_count_before > 0:
                # Delete all documents
                delete_result = await collection.delete_many({})
                deleted_count = delete_result.deleted_count
                
                # Verify deletion
                doc_count_after = await collection.count_documents({})
                
                if doc_count_after == 0:
                    logger.info(f"✅ Successfully cleared {deleted_count} documents from {collection_name}")
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
            else:
                logger.info(f"Collection {collection_name} was already empty")
                results[collection_name] = {
                    'documents_before': 0,
                    'documents_deleted': 0,
                    'documents_after': 0,
                    'status': 'already_empty'
                }
        
        return results
        
    except Exception as e:
        logger.error(f"❌ Error during collection clearing: {e}")
        return None
    
    finally:
        # Close database connection
        await close_mongo_connection()
        logger.info("Database connection closed")

def print_summary(results):
    """
    Print a formatted summary of the clearing operation.
    
    Args:
        results (dict): Results from the clearing operation
    """
    if not results:
        print("\n❌ OPERATION FAILED")
        print("Unable to clear collections due to errors.")
        return
    
    print("\n" + "="*60)
    print("JOURNEY DATA CLEARING SUMMARY")
    print("="*60)
    
    total_deleted = 0
    
    for collection_name, result in results.items():
        status_icon = {
            'success': '✅',
            'partial': '⚠️',
            'already_empty': 'ℹ️'
        }.get(result['status'], '❓')
        
        print(f"\n{status_icon} Collection: {collection_name}")
        print(f"   Documents before: {result['documents_before']}")
        print(f"   Documents deleted: {result['documents_deleted']}")
        print(f"   Documents after: {result['documents_after']}")
        print(f"   Status: {result['status'].replace('_', ' ').title()}")
        
        total_deleted += result['documents_deleted']
    
    print(f"\n📊 TOTAL DOCUMENTS DELETED: {total_deleted}")
    print("="*60)
    
    # Safety confirmation
    if total_deleted > 0:
        print("\n⚠️  IMPORTANT: This operation cannot be undone.")
        print("   Make sure you have backups if this data is needed.")
    
    print("\n✅ Operation completed successfully!")

async def main():
    """
    Main function to execute the clearing operation.
    """
    print("🧹 Journey Data Clearing Script")
    print("="*40)
    print("This script will clear ALL documents from:")
    print("- journey_reflections collection")
    print("- journey_insights collection")
    print("\n⚠️  WARNING: This operation cannot be undone!")
    
    # Ask for confirmation
    try:
        confirmation = input("\nDo you want to proceed? (yes/no): ").strip().lower()
        if confirmation not in ['yes', 'y']:
            print("Operation cancelled by user.")
            return
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        return
    
    print("\nStarting clearing operation...")
    
    # Execute the clearing operation
    results = await clear_journey_collections()
    
    # Print summary
    print_summary(results)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nOperation interrupted by user.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)