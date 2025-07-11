"""
Sprint S10.1 Foundation Migration Script

This script handles the database schema changes for the Sprint S10 redesign:
1. Rename session_insights collection to entries
2. Rename goals collection to destinations  
3. Create new collections: quotes, small_steps, coach_resources, user_quote_likes, coach_client_notes
4. Add new fields to existing collections (profiles, coaching_relationships)
5. Provide rollback capability

Usage:
    python -m backend.migrations.s10_1_foundation_migration migrate
    python -m backend.migrations.s10_1_foundation_migration rollback
    python -m backend.migrations.s10_1_foundation_migration validate
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import IndexModel
import os
import sys

# Add the backend directory to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.core.config import settings
from app.db.mongodb import get_database

logger = logging.getLogger(__name__)


class S10FoundationMigration:
    def __init__(self):
        self.db = None
        self.backup_collections = {}

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

    async def migrate_session_insights_to_entries(self):
        """Migrate session_insights collection to entries with new fields"""
        logger.info("=== Migrating session_insights to entries ===")
        
        try:
            # Check if session_insights collection exists
            collections = await self.db.list_collection_names()
            if "session_insights" not in collections:
                logger.info("session_insights collection not found, skipping migration")
                return
            
            # Create backup
            await self._backup_collection("session_insights")
            
            # Get all documents from session_insights
            session_insights = []
            async for doc in self.db.session_insights.find():
                session_insights.append(doc)
            
            logger.info(f"Found {len(session_insights)} session insights to migrate")
            
            if not session_insights:
                logger.info("No session insights to migrate")
                return
            
            # Transform documents for entries collection
            entries = []
            for insight in session_insights:
                entry = insight.copy()
                
                # Add new fields
                entry["entry_type"] = "session"  # All existing insights are session type
                entry["title"] = insight.get("session_title") or f"Session from {insight.get('session_date', 'Unknown Date')}"
                entry["transcript_content"] = insight.get("transcript_content")
                entry["content"] = None  # Only for fresh thoughts
                entry["detected_goals"] = []  # Empty initially, will be populated by AI
                
                # Rename celebrations field to match new structure
                if "celebration" in entry:
                    entry["celebrations"] = [entry.pop("celebration")] if entry["celebration"] else []
                else:
                    entry["celebrations"] = []
                
                # Rename intention field to match new structure  
                if "intention" in entry:
                    entry["intentions"] = [entry.pop("intention")] if entry["intention"] else []
                else:
                    entry["intentions"] = []
                
                entries.append(entry)
            
            # Create entries collection and insert documents
            if entries:
                await self.db.entries.insert_many(entries)
                logger.info(f"✅ Migrated {len(entries)} documents to entries collection")
            
            # Create indexes for entries collection
            await self._create_entries_indexes()
            
        except Exception as e:
            logger.error(f"❌ Error migrating session_insights to entries: {e}")
            raise

    async def migrate_goals_to_destinations(self):
        """Migrate goals collection to destinations with new fields"""
        logger.info("=== Migrating goals to destinations ===")
        
        try:
            # Check if goals collection exists
            collections = await self.db.list_collection_names()
            if "goals" not in collections:
                logger.info("goals collection not found, skipping migration")
                return
            
            # Create backup
            await self._backup_collection("goals")
            
            # Get all documents from goals
            goals = []
            async for doc in self.db.goals.find():
                goals.append(doc)
            
            logger.info(f"Found {len(goals)} goals to migrate")
            
            if not goals:
                logger.info("No goals to migrate")
                return
            
            # Transform documents for destinations collection
            destinations = []
            for goal in goals:
                destination = goal.copy()
                
                # Rename goal_statement to destination_statement
                if "goal_statement" in destination:
                    destination["destination_statement"] = destination.pop("goal_statement")
                elif "title" in destination:
                    destination["destination_statement"] = destination.pop("title")
                
                # Add new fields with defaults
                destination["is_big_idea"] = False
                destination["big_idea_rank"] = None
                destination["priority"] = "medium"
                destination["category"] = "personal"
                destination["source_entries"] = []
                
                # Ensure progress_history exists
                if "progress_history" not in destination:
                    destination["progress_history"] = []
                
                destinations.append(destination)
            
            # Create destinations collection and insert documents
            if destinations:
                await self.db.destinations.insert_many(destinations)
                logger.info(f"✅ Migrated {len(destinations)} documents to destinations collection")
            
            # Create indexes for destinations collection
            await self._create_destinations_indexes()
            
        except Exception as e:
            logger.error(f"❌ Error migrating goals to destinations: {e}")
            raise

    async def create_new_collections(self):
        """Create all new collections with indexes"""
        logger.info("=== Creating new collections ===")
        
        try:
            # Create quotes collection with sample data
            await self._create_quotes_collection()
            
            # Create user_quote_likes collection
            await self._create_user_quote_likes_collection()
            
            # Create small_steps collection
            await self._create_small_steps_collection()
            
            # Create coach_resources collection
            await self._create_coach_resources_collection()
            
            # Create coach_client_notes collection
            await self._create_coach_client_notes_collection()
            
            logger.info("✅ Successfully created all new collections")
            
        except Exception as e:
            logger.error(f"❌ Error creating new collections: {e}")
            raise

    async def enhance_existing_collections(self):
        """Add new fields to existing collections"""
        logger.info("=== Enhancing existing collections ===")
        
        try:
            # Enhance profiles collection
            await self._enhance_profiles_collection()
            
            # Enhance coaching_relationships collection
            await self._enhance_coaching_relationships_collection()
            
            logger.info("✅ Successfully enhanced existing collections")
            
        except Exception as e:
            logger.error(f"❌ Error enhancing existing collections: {e}")
            raise

    async def _backup_collection(self, collection_name: str):
        """Create a backup of a collection"""
        try:
            backup_name = f"{collection_name}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Copy all documents to backup collection
            documents = []
            async for doc in self.db[collection_name].find():
                documents.append(doc)
            
            if documents:
                await self.db[backup_name].insert_many(documents)
                self.backup_collections[collection_name] = backup_name
                logger.info(f"✅ Created backup: {backup_name} ({len(documents)} documents)")
            else:
                logger.info(f"No documents to backup in {collection_name}")
                
        except Exception as e:
            logger.error(f"❌ Error creating backup for {collection_name}: {e}")
            raise

    async def _create_entries_indexes(self):
        """Create indexes for entries collection"""
        indexes = [
            IndexModel([("client_user_id", 1), ("created_at", -1)]),
            IndexModel([("coaching_relationship_id", 1), ("session_date", -1)]),
            IndexModel([("entry_type", 1)]),
            IndexModel([("status", 1)]),
            IndexModel([("tags", 1)])
        ]
        await self.db.entries.create_indexes(indexes)
        logger.info("✅ Created indexes for entries collection")

    async def _create_destinations_indexes(self):
        """Create indexes for destinations collection"""
        indexes = [
            IndexModel([("user_id", 1), ("created_at", -1)]),
            IndexModel([("is_big_idea", 1), ("big_idea_rank", 1)]),
            IndexModel([("priority", 1)]),
            IndexModel([("category", 1)]),
            IndexModel([("status", 1)]),
            IndexModel([("tags", 1)])
        ]
        await self.db.destinations.create_indexes(indexes)
        logger.info("✅ Created indexes for destinations collection")

    async def _create_quotes_collection(self):
        """Create quotes collection with sample data"""
        # Sample quotes for initial population
        sample_quotes = [
            {
                "quote_text": "The only way to do great work is to love what you do.",
                "author": "Steve Jobs",
                "source": "Stanford Commencement Address",
                "category": "motivation",
                "tags": ["work", "passion", "success"],
                "display_count": 0,
                "like_count": 0,
                "active": True,
                "created_by": "system",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "quote_text": "Leadership is not about being in charge. It's about taking care of those in your charge.",
                "author": "Simon Sinek",
                "source": "Leaders Eat Last",
                "category": "leadership",
                "tags": ["leadership", "care", "responsibility"],
                "display_count": 0,
                "like_count": 0,
                "active": True,
                "created_by": "system",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "quote_text": "Growth begins at the end of your comfort zone.",
                "author": "Neale Donald Walsch",
                "source": None,
                "category": "growth",
                "tags": ["growth", "comfort zone", "challenge"],
                "display_count": 0,
                "like_count": 0,
                "active": True,
                "created_by": "system",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "quote_text": "Courage is not the absence of fear, but action in spite of it.",
                "author": "Mark Twain",
                "source": None,
                "category": "courage",
                "tags": ["courage", "fear", "action"],
                "display_count": 0,
                "like_count": 0,
                "active": True,
                "created_by": "system",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]
        
        await self.db.quotes.insert_many(sample_quotes)
        
        # Create indexes
        indexes = [
            IndexModel([("category", 1)]),
            IndexModel([("active", 1)]),
            IndexModel([("tags", 1)]),
            IndexModel([("like_count", -1)])
        ]
        await self.db.quotes.create_indexes(indexes)
        logger.info(f"✅ Created quotes collection with {len(sample_quotes)} sample quotes")

    async def _create_user_quote_likes_collection(self):
        """Create user_quote_likes collection"""
        indexes = [
            IndexModel([("user_id", 1), ("quote_id", 1)], unique=True),
            IndexModel([("user_id", 1)]),
            IndexModel([("quote_id", 1)])
        ]
        await self.db.user_quote_likes.create_indexes(indexes)
        logger.info("✅ Created user_quote_likes collection")

    async def _create_small_steps_collection(self):
        """Create small_steps collection"""
        indexes = [
            IndexModel([("user_id", 1), ("created_at", -1)]),
            IndexModel([("source_entry_id", 1)]),
            IndexModel([("related_destination_id", 1)]),
            IndexModel([("completed", 1)])
        ]
        await self.db.small_steps.create_indexes(indexes)
        logger.info("✅ Created small_steps collection")

    async def _create_coach_resources_collection(self):
        """Create coach_resources collection"""
        indexes = [
            IndexModel([("coach_user_id", 1), ("created_at", -1)]),
            IndexModel([("category", 1)]),
            IndexModel([("resource_type", 1)]),
            IndexModel([("is_template", 1)]),
            IndexModel([("client_specific", 1), ("target_client_id", 1)]),
            IndexModel([("active", 1)])
        ]
        await self.db.coach_resources.create_indexes(indexes)
        logger.info("✅ Created coach_resources collection")

    async def _create_coach_client_notes_collection(self):
        """Create coach_client_notes collection"""
        indexes = [
            IndexModel([("coach_user_id", 1), ("client_user_id", 1)], unique=True),
            IndexModel([("coach_user_id", 1)]),
            IndexModel([("client_user_id", 1)])
        ]
        await self.db.coach_client_notes.create_indexes(indexes)
        logger.info("✅ Created coach_client_notes collection")

    async def _enhance_profiles_collection(self):
        """Add new fields to profiles collection"""
        # Add new fields to all existing profiles
        update_result = await self.db.profiles.update_many(
            {"identity_foundation": {"$exists": False}},
            {
                "$set": {
                    "identity_foundation": None,
                    "freemium_status": {
                        "has_coach": False,
                        "entries_count": 0,
                        "max_free_entries": 3,
                        "coach_requested": False,
                        "coach_request_date": None
                    },
                    "dashboard_preferences": {
                        "preferred_landing_tab": "journey",
                        "quote_likes": [],
                        "onboarding_completed": False,
                        "tooltips_shown": False
                    },
                    "redesign_features": {
                        "unified_entries": False,
                        "destinations_rebrand": False,
                        "mountain_navigation": False,
                        "freemium_gating": False
                    },
                    "updated_at": datetime.utcnow()
                }
            }
        )
        logger.info(f"✅ Enhanced {update_result.modified_count} profiles with new fields")

    async def _enhance_coaching_relationships_collection(self):
        """Add new fields to coaching_relationships collection"""
        # Add new fields to all existing coaching relationships
        update_result = await self.db.coaching_relationships.update_many(
            {"invited_by_email": {"$exists": False}},
            {
                "$set": {
                    "invited_by_email": None,
                    "invitation_accepted_at": None,
                    "upgraded_from_freemium": False,
                    "upgrade_date": None,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        logger.info(f"✅ Enhanced {update_result.modified_count} coaching relationships with new fields")

    async def validate_migration(self):
        """Validate migration success"""
        logger.info("=== Validating migration ===")
        
        try:
            validation_results = {}
            
            # Check document counts
            collections = await self.db.list_collection_names()
            
            if "session_insights" in collections and "entries" in collections:
                session_insights_count = await self.db.session_insights.count_documents({})
                entries_count = await self.db.entries.count_documents({})
                validation_results["session_insights_to_entries"] = {
                    "original_count": session_insights_count,
                    "migrated_count": entries_count,
                    "success": session_insights_count == entries_count
                }
            
            if "goals" in collections and "destinations" in collections:
                goals_count = await self.db.goals.count_documents({})
                destinations_count = await self.db.destinations.count_documents({})
                validation_results["goals_to_destinations"] = {
                    "original_count": goals_count,
                    "migrated_count": destinations_count,
                    "success": goals_count == destinations_count
                }
            
            # Check new collections exist
            required_new_collections = ["quotes", "user_quote_likes", "small_steps", "coach_resources", "coach_client_notes"]
            for collection_name in required_new_collections:
                validation_results[f"new_collection_{collection_name}"] = {
                    "exists": collection_name in collections
                }
            
            # Check sample data in quotes
            quotes_count = await self.db.quotes.count_documents({})
            validation_results["quotes_sample_data"] = {
                "count": quotes_count,
                "has_sample_data": quotes_count > 0
            }
            
            # Validate indexes
            for collection_name in ["entries", "destinations", "quotes", "user_quote_likes", "small_steps", "coach_resources", "coach_client_notes"]:
                if collection_name in collections:
                    indexes = await self.db[collection_name].list_indexes().to_list(length=None)
                    validation_results[f"{collection_name}_indexes"] = {
                        "count": len(indexes),
                        "has_indexes": len(indexes) > 1  # More than just the default _id index
                    }
            
            # Print validation results
            logger.info("=== Validation Results ===")
            all_successful = True
            for key, result in validation_results.items():
                if isinstance(result, dict):
                    if "success" in result:
                        status = "✅" if result["success"] else "❌"
                        logger.info(f"{status} {key}: {result}")
                        if not result["success"]:
                            all_successful = False
                    elif "exists" in result:
                        status = "✅" if result["exists"] else "❌"
                        logger.info(f"{status} {key}: exists = {result['exists']}")
                        if not result["exists"]:
                            all_successful = False
                    else:
                        logger.info(f"ℹ️  {key}: {result}")
            
            if all_successful:
                logger.info("✅ All validations passed!")
            else:
                logger.warning("⚠️  Some validations failed")
            
            return validation_results
            
        except Exception as e:
            logger.error(f"❌ Error during validation: {e}")
            raise

    async def rollback_migration(self):
        """Rollback migration if needed"""
        logger.info("=== Rolling back migration ===")
        
        try:
            # Restore original collections from backups
            for original_name, backup_name in self.backup_collections.items():
                collections = await self.db.list_collection_names()
                if backup_name in collections:
                    # Drop current collection
                    await self.db[original_name].drop()
                    
                    # Restore from backup
                    documents = []
                    async for doc in self.db[backup_name].find():
                        documents.append(doc)
                    
                    if documents:
                        await self.db[original_name].insert_many(documents)
                        logger.info(f"✅ Restored {original_name} from {backup_name} ({len(documents)} documents)")
                    
                    # Drop backup collection
                    await self.db[backup_name].drop()
            
            # Remove new collections
            new_collections = ["entries", "destinations", "quotes", "user_quote_likes", "small_steps", "coach_resources", "coach_client_notes"]
            collections = await self.db.list_collection_names()
            
            for collection_name in new_collections:
                if collection_name in collections:
                    await self.db[collection_name].drop()
                    logger.info(f"✅ Dropped new collection: {collection_name}")
            
            # Restore original profile fields (remove new fields)
            await self.db.profiles.update_many(
                {},
                {
                    "$unset": {
                        "identity_foundation": "",
                        "freemium_status": "",
                        "dashboard_preferences": "",
                        "redesign_features": ""
                    },
                    "$set": {
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            # Restore original coaching relationship fields
            await self.db.coaching_relationships.update_many(
                {},
                {
                    "$unset": {
                        "invited_by_email": "",
                        "invitation_accepted_at": "",
                        "upgraded_from_freemium": "",
                        "upgrade_date": ""
                    },
                    "$set": {
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            logger.info("✅ Migration rollback completed")
            
        except Exception as e:
            logger.error(f"❌ Error during rollback: {e}")
            raise

    async def run_migration(self):
        """Run the complete migration"""
        logger.info("🚀 Starting Sprint S10.1 Foundation Migration")
        
        try:
            await self.connect()
            
            # Step 1: Migrate session_insights to entries
            await self.migrate_session_insights_to_entries()
            
            # Step 2: Migrate goals to destinations
            await self.migrate_goals_to_destinations()
            
            # Step 3: Create new collections
            await self.create_new_collections()
            
            # Step 4: Enhance existing collections
            await self.enhance_existing_collections()
            
            # Step 5: Validate migration
            await self.validate_migration()
            
            logger.info("🎉 Migration completed successfully!")
            
        except Exception as e:
            logger.error(f"💥 Migration failed: {e}")
            logger.info("Consider running rollback if needed")
            raise


async def main():
    """Main function to run migration commands"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Sprint S10.1 Foundation Migration")
    parser.add_argument("command", choices=["migrate", "rollback", "validate"], 
                       help="Migration command to run")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    migration = S10FoundationMigration()
    
    try:
        if args.command == "migrate":
            await migration.run_migration()
        elif args.command == "rollback":
            await migration.connect()
            await migration.rollback_migration()
        elif args.command == "validate":
            await migration.connect()
            await migration.validate_migration()
            
    except Exception as e:
        logger.error(f"Command failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())