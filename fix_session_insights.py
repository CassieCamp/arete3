#!/usr/bin/env python3
"""
Quick fix script for session insight validation errors.
This script directly connects to MongoDB Atlas and fixes the missing required fields.
"""

import asyncio
import logging
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# MongoDB Atlas connection string from .env
DATABASE_URL = "mongodb+srv://cassie:mSt2YiY^hjgX@arete.6cwmnzs.mongodb.net/?retryWrites=true&w=majority&appName=Arete"
DATABASE_NAME = "arete_mvp"

async def fix_session_insights():
    """Fix session insight records with missing required fields"""
    
    # Connection options for Atlas
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
    
    try:
        # Connect to MongoDB Atlas
        logger.info("Connecting to MongoDB Atlas...")
        client = AsyncIOMotorClient(DATABASE_URL, **connection_options)
        db = client[DATABASE_NAME]
        
        # Test connection
        await client.admin.command('ping')
        logger.info("✅ Connected to MongoDB Atlas")
        
        # Find session insight entries that need fixing
        query = {
            "entry_type": "session",
            "$or": [
                {"transcript_source": {"$exists": False}},
                {"session_summary": {"$exists": False}},
                {"created_by": {"$exists": False}},
                {"overall_session_quality": None},
                {"metadata.transcript_word_count": {"$exists": False}},
                {"metadata.ai_provider": {"$exists": False}},
                {"metadata.model_version": {"$exists": False}},
                {"metadata.processing_time_seconds": {"$exists": False}},
                {"metadata.analysis_confidence": {"$exists": False}},
                {"metadata": {"$exists": False}},
                {"metadata": None}
            ]
        }
        
        entries_to_fix = []
        async for entry in db.entries.find(query):
            entries_to_fix.append(entry)
        
        logger.info(f"Found {len(entries_to_fix)} session insight entries that need fixing")
        
        if not entries_to_fix:
            logger.info("No entries need fixing!")
            return
        
        # Fix each entry
        fixed_count = 0
        for entry in entries_to_fix:
            entry_id = entry["_id"]
            logger.info(f"Fixing entry: {entry_id}")
            
            # Prepare update fields
            update_fields = {}
            
            # Add missing transcript_source
            if "transcript_source" not in entry:
                update_fields["transcript_source"] = "unknown"
            
            # Add missing session_summary
            if "session_summary" not in entry:
                update_fields["session_summary"] = "No summary available."
            
            # Add missing created_by - try to find a valid user ID
            if "created_by" not in entry:
                created_by = "system_generated"
                
                # Try to find user ID from client_user_id
                if "client_user_id" in entry and entry["client_user_id"]:
                    created_by = entry["client_user_id"]
                # Try to find user ID from coach_user_id
                elif "coach_user_id" in entry and entry["coach_user_id"]:
                    created_by = entry["coach_user_id"]
                
                update_fields["created_by"] = created_by
            
            # Fix overall_session_quality if it's None
            if entry.get("overall_session_quality") is None:
                update_fields["overall_session_quality"] = "Not rated"
            
            # Fix metadata fields if they're missing or empty
            metadata = entry.get("metadata", {})
            if not metadata or not isinstance(metadata, dict):
                metadata = {}
            
            metadata_updates = {}
            if "transcript_word_count" not in metadata:
                metadata_updates["transcript_word_count"] = 0
            if "ai_provider" not in metadata:
                metadata_updates["ai_provider"] = "unknown"
            if "model_version" not in metadata:
                metadata_updates["model_version"] = "unknown"
            if "processing_time_seconds" not in metadata:
                metadata_updates["processing_time_seconds"] = 0.0
            if "analysis_confidence" not in metadata:
                metadata_updates["analysis_confidence"] = 0.0
            
            if metadata_updates:
                metadata.update(metadata_updates)
                update_fields["metadata"] = metadata
            
            # Update the entry
            if update_fields:
                update_fields["updated_at"] = datetime.utcnow()
                result = await db.entries.update_one(
                    {"_id": entry_id},
                    {"$set": update_fields}
                )
                
                if result.modified_count > 0:
                    fixed_count += 1
                    logger.info(f"✅ Fixed entry {entry_id}: {list(update_fields.keys())}")
                else:
                    logger.warning(f"⚠️  Failed to update entry {entry_id}")
        
        logger.info(f"🎉 Successfully fixed {fixed_count} out of {len(entries_to_fix)} entries")
        
        # Verify the fix by checking the specific problematic entry
        problematic_id = "68707d61733cb43823cbd067"
        try:
            problematic_entry = await db.entries.find_one({"_id": problematic_id})
            if problematic_entry:
                logger.info(f"✅ Verified problematic entry {problematic_id}:")
                logger.info(f"   - transcript_source: {problematic_entry.get('transcript_source', 'MISSING')}")
                logger.info(f"   - session_summary: {problematic_entry.get('session_summary', 'MISSING')}")
                logger.info(f"   - created_by: {problematic_entry.get('created_by', 'MISSING')}")
                logger.info(f"   - overall_session_quality: {problematic_entry.get('overall_session_quality', 'MISSING')}")
            else:
                logger.warning(f"⚠️  Could not find entry with ID {problematic_id}")
        except Exception as e:
            logger.error(f"Error checking problematic entry: {e}")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        raise
    finally:
        if 'client' in locals():
            client.close()
            logger.info("Disconnected from MongoDB")

if __name__ == "__main__":
    asyncio.run(fix_session_insights())