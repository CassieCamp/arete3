"""
Sprint S10.2 Fix Session Insights Migration Script

This script fixes session insight records in the entries collection that are missing required fields
due to incomplete data migration. It updates records with default values for missing fields.

Usage:
    python -m backend.migrations.s10_2_fix_insights_migration migrate
    python -m backend.migrations.s10_2_fix_insights_migration validate
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List
from motor.motor_asyncio import AsyncIOMotorClient
import os
import sys

# Add the backend directory to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.core.config import settings
from app.db.mongodb import get_database

logger = logging.getLogger(__name__)


class S10FixInsightsMigration:
    def __init__(self):
        self.db = None
        self.fixed_count = 0
        self.error_count = 0

    async def connect(self):
        """Connect to the database"""
        try:
            self.db = get_database()
            if not self.db:
                raise Exception("Failed to connect to database")
            logger.info("✅ Connected to database")
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            raise

    async def find_incomplete_session_insights(self):
        """Find session insight records missing required fields"""
        logger.info("=== Finding incomplete session insight records ===")
        
        try:
            # Check if entries collection exists
            collections = await self.db.list_collection_names()
            if "entries" not in collections:
                logger.info("entries collection not found, nothing to fix")
                return []
            
            # Find session insight entries missing required fields
            query = {
                "entry_type": "session_insight",
                "$or": [
                    {"transcript_source": {"$exists": False}},
                    {"session_summary": {"$exists": False}},
                    {"created_by": {"$exists": False}},
                    {"overall_session_quality": {"$exists": False}}
                ]
            }
            
            incomplete_records = []
            async for doc in self.db.entries.find(query):
                incomplete_records.append(doc)
            
            logger.info(f"Found {len(incomplete_records)} incomplete session insight records")
            return incomplete_records
            
        except Exception as e:
            logger.error(f"❌ Error finding incomplete records: {e}")
            raise

    async def get_user_id_for_record(self, record: Dict[str, Any]) -> str:
        """Get user_id for created_by field from related user record"""
        try:
            # Try to get user_id from the record itself
            if "client_user_id" in record and record["client_user_id"]:
                # Verify the user exists
                user = await self.db.users.find_one({"user_id": record["client_user_id"]})
                if user:
                    return record["client_user_id"]
            
            # If coach_user_id exists, try that
            if "coach_user_id" in record and record["coach_user_id"]:
                user = await self.db.users.find_one({"user_id": record["coach_user_id"]})
                if user:
                    return record["coach_user_id"]
            
            # If we have a coaching_relationship_id, try to get user from there
            if "coaching_relationship_id" in record and record["coaching_relationship_id"]:
                relationship = await self.db.coaching_relationships.find_one(
                    {"_id": record["coaching_relationship_id"]}
                )
                if relationship:
                    if "client_user_id" in relationship:
                        user = await self.db.users.find_one({"user_id": relationship["client_user_id"]})
                        if user:
                            return relationship["client_user_id"]
                    if "coach_user_id" in relationship:
                        user = await self.db.users.find_one({"user_id": relationship["coach_user_id"]})
                        if user:
                            return relationship["coach_user_id"]
            
            # Fallback to system_generated
            logger.warning(f"Could not find valid user for record {record.get('_id')}, using system_generated")
            return "system_generated"
            
        except Exception as e:
            logger.error(f"❌ Error getting user_id for record {record.get('_id')}: {e}")
            return "system_generated"

    async def fix_incomplete_record(self, record: Dict[str, Any]):
        """Fix a single incomplete record by adding missing fields"""
        try:
            record_id = record["_id"]
            updates = {}
            
            # Add missing transcript_source
            if "transcript_source" not in record or not record.get("transcript_source"):
                updates["transcript_source"] = "unknown"
            
            # Add missing session_summary
            if "session_summary" not in record or not record.get("session_summary"):
                updates["session_summary"] = "No summary available."
            
            # Add missing created_by
            if "created_by" not in record or not record.get("created_by"):
                user_id = await self.get_user_id_for_record(record)
                updates["created_by"] = user_id
            
            # Add missing overall_session_quality
            if "overall_session_quality" not in record or not record.get("overall_session_quality"):
                updates["overall_session_quality"] = "Not rated"
            
            # Update the record if we have changes
            if updates:
                updates["updated_at"] = datetime.utcnow()
                
                result = await self.db.entries.update_one(
                    {"_id": record_id},
                    {"$set": updates}
                )
                
                if result.modified_count > 0:
                    self.fixed_count += 1
                    logger.info(f"✅ Fixed record {record_id} with updates: {list(updates.keys())}")
                else:
                    logger.warning(f"⚠️  No changes made to record {record_id}")
            else:
                logger.info(f"ℹ️  Record {record_id} already has all required fields")
                
        except Exception as e:
            self.error_count += 1
            logger.error(f"❌ Error fixing record {record.get('_id')}: {e}")

    async def fix_all_incomplete_records(self):
        """Fix all incomplete session insight records"""
        logger.info("=== Fixing incomplete session insight records ===")
        
        try:
            # Find all incomplete records
            incomplete_records = await self.find_incomplete_session_insights()
            
            if not incomplete_records:
                logger.info("No incomplete records found to fix")
                return
            
            # Fix each record
            for record in incomplete_records:
                await self.fix_incomplete_record(record)
            
            logger.info(f"✅ Migration completed: {self.fixed_count} records fixed, {self.error_count} errors")
            
        except Exception as e:
            logger.error(f"❌ Error during migration: {e}")
            raise

    async def validate_migration(self):
        """Validate that all session insight records now have required fields"""
        logger.info("=== Validating migration ===")
        
        try:
            # Check if entries collection exists
            collections = await self.db.list_collection_names()
            if "entries" not in collections:
                logger.info("entries collection not found, nothing to validate")
                return
            
            # Count total session insight records
            total_session_insights = await self.db.entries.count_documents({
                "entry_type": "session_insight"
            })
            
            # Count records still missing required fields
            missing_transcript_source = await self.db.entries.count_documents({
                "entry_type": "session_insight",
                "$or": [
                    {"transcript_source": {"$exists": False}},
                    {"transcript_source": None},
                    {"transcript_source": ""}
                ]
            })
            
            missing_session_summary = await self.db.entries.count_documents({
                "entry_type": "session_insight",
                "$or": [
                    {"session_summary": {"$exists": False}},
                    {"session_summary": None},
                    {"session_summary": ""}
                ]
            })
            
            missing_created_by = await self.db.entries.count_documents({
                "entry_type": "session_insight",
                "$or": [
                    {"created_by": {"$exists": False}},
                    {"created_by": None},
                    {"created_by": ""}
                ]
            })
            
            missing_quality = await self.db.entries.count_documents({
                "entry_type": "session_insight",
                "$or": [
                    {"overall_session_quality": {"$exists": False}},
                    {"overall_session_quality": None},
                    {"overall_session_quality": ""}
                ]
            })
            
            # Print validation results
            logger.info("=== Validation Results ===")
            logger.info(f"Total session insight records: {total_session_insights}")
            logger.info(f"Missing transcript_source: {missing_transcript_source}")
            logger.info(f"Missing session_summary: {missing_session_summary}")
            logger.info(f"Missing created_by: {missing_created_by}")
            logger.info(f"Missing overall_session_quality: {missing_quality}")
            
            total_missing = missing_transcript_source + missing_session_summary + missing_created_by + missing_quality
            
            if total_missing == 0:
                logger.info("✅ All session insight records have required fields!")
                return True
            else:
                logger.warning(f"⚠️  {total_missing} field instances still missing")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error during validation: {e}")
            raise

    async def run_migration(self):
        """Run the complete migration"""
        logger.info("🚀 Starting Sprint S10.2 Fix Session Insights Migration")
        
        try:
            await self.connect()
            
            # Fix incomplete records
            await self.fix_all_incomplete_records()
            
            # Validate migration
            validation_success = await self.validate_migration()
            
            if validation_success:
                logger.info("🎉 Migration completed successfully!")
            else:
                logger.warning("⚠️  Migration completed with some issues - check validation results")
            
        except Exception as e:
            logger.error(f"💥 Migration failed: {e}")
            raise


async def main():
    """Main function to run migration commands"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Sprint S10.2 Fix Session Insights Migration")
    parser.add_argument("command", choices=["migrate", "validate"], 
                       help="Migration command to run")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    migration = S10FixInsightsMigration()
    
    try:
        if args.command == "migrate":
            await migration.run_migration()
        elif args.command == "validate":
            await migration.connect()
            await migration.validate_migration()
            
    except Exception as e:
        logger.error(f"Command failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())