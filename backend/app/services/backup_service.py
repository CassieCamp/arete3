from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from bson import ObjectId
from app.models.coaching_relationship import CoachingRelationship
from app.models.audit_log import AuditOperation, AuditSeverity
from app.repositories.audit_repository import AuditRepository
from app.db.mongodb import get_database
import logging
import json
import os

logger = logging.getLogger(__name__)


class BackupService:
    """
    Service for creating and managing backups of critical data
    """
    
    def __init__(self):
        self.audit_repository = AuditRepository()
        self.backup_collection = "relationship_backups"

    async def backup_active_relationships(self) -> Dict[str, Any]:
        """Create a backup of all active coaching relationships"""
        logger.info("=== BackupService.backup_active_relationships called ===")
        
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                raise Exception("Database connection is None")

            # Get all active relationships (not soft deleted)
            query = {
                "$and": [
                    {"status": {"$ne": "deleted"}},
                    {"deleted_at": {"$exists": False}}
                ]
            }
            
            cursor = db["coaching_relationships"].find(query)
            relationships = await cursor.to_list(length=None)
            
            # Convert ObjectIds to strings for JSON serialization
            for rel in relationships:
                if "_id" in rel:
                    rel["_id"] = str(rel["_id"])
                # Convert datetime objects to ISO strings
                for field in ["created_at", "updated_at", "deleted_at"]:
                    if field in rel and rel[field]:
                        rel[field] = rel[field].isoformat() if isinstance(rel[field], datetime) else rel[field]

            # Create backup document
            backup_data = {
                "backup_type": "active_relationships",
                "timestamp": datetime.utcnow(),
                "relationship_count": len(relationships),
                "relationships": relationships,
                "environment": os.getenv("ENVIRONMENT", "development"),
                "backup_version": "1.0"
            }

            # Store backup in database
            result = await db[self.backup_collection].insert_one(backup_data)
            backup_id = str(result.inserted_id)

            # Log successful backup
            await self.audit_repository.log_operation(
                operation=AuditOperation.BACKUP_CREATED,
                severity=AuditSeverity.INFO,
                entity_type="coaching_relationship",
                message=f"Successfully created backup of {len(relationships)} active relationships",
                operation_details={
                    "backup_id": backup_id,
                    "relationship_count": len(relationships),
                    "backup_type": "active_relationships"
                },
                tags=["backup", "daily_backup"]
            )

            logger.info(f"✅ Successfully created backup {backup_id} with {len(relationships)} relationships")
            
            return {
                "backup_id": backup_id,
                "relationship_count": len(relationships),
                "timestamp": backup_data["timestamp"],
                "success": True
            }

        except Exception as e:
            # Log backup failure
            await self.audit_repository.log_critical_operation(
                operation=AuditOperation.BACKUP_CREATED,
                entity_type="coaching_relationship",
                message=f"Failed to create relationship backup: {str(e)}",
                error_message=str(e)
            )
            
            logger.error(f"❌ Error in backup_active_relationships: {e}")
            raise

    async def restore_relationships_from_backup(self, backup_id: str, restore_user_id: str) -> Dict[str, Any]:
        """Restore relationships from a specific backup"""
        logger.critical(f"🚨 RELATIONSHIP RESTORE ATTEMPTED: backup_id={backup_id} by user={restore_user_id}")
        
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                raise Exception("Database connection is None")

            # Get backup data
            backup_doc = await db[self.backup_collection].find_one({"_id": ObjectId(backup_id)})
            if not backup_doc:
                raise ValueError(f"Backup {backup_id} not found")

            relationships_to_restore = backup_doc.get("relationships", [])
            
            # Log restore attempt
            await self.audit_repository.log_critical_operation(
                operation=AuditOperation.BACKUP_RESTORED,
                entity_type="coaching_relationship",
                message=f"Attempting to restore {len(relationships_to_restore)} relationships from backup {backup_id}",
                user_id=restore_user_id,
                operation_details={
                    "backup_id": backup_id,
                    "relationship_count": len(relationships_to_restore),
                    "backup_timestamp": backup_doc.get("timestamp")
                }
            )

            restored_count = 0
            skipped_count = 0
            
            for rel_data in relationships_to_restore:
                try:
                    # Check if relationship already exists
                    existing = await db["coaching_relationships"].find_one({
                        "coach_user_id": rel_data["coach_user_id"],
                        "client_user_id": rel_data["client_user_id"]
                    })
                    
                    if existing:
                        skipped_count += 1
                        continue
                    
                    # Prepare relationship for insertion
                    rel_data_copy = rel_data.copy()
                    if "_id" in rel_data_copy:
                        del rel_data_copy["_id"]  # Let MongoDB generate new ID
                    
                    # Convert ISO strings back to datetime objects
                    for field in ["created_at", "updated_at", "deleted_at"]:
                        if field in rel_data_copy and rel_data_copy[field]:
                            if isinstance(rel_data_copy[field], str):
                                rel_data_copy[field] = datetime.fromisoformat(rel_data_copy[field].replace('Z', '+00:00'))
                    
                    # Insert relationship
                    await db["coaching_relationships"].insert_one(rel_data_copy)
                    restored_count += 1
                    
                except Exception as rel_error:
                    logger.error(f"Failed to restore individual relationship: {rel_error}")
                    continue

            # Log restore completion
            await self.audit_repository.log_critical_operation(
                operation=AuditOperation.BACKUP_RESTORED,
                entity_type="coaching_relationship",
                message=f"Restore completed: {restored_count} restored, {skipped_count} skipped",
                user_id=restore_user_id,
                operation_details={
                    "backup_id": backup_id,
                    "restored_count": restored_count,
                    "skipped_count": skipped_count
                }
            )

            logger.info(f"✅ Restore completed: {restored_count} restored, {skipped_count} skipped")
            
            return {
                "backup_id": backup_id,
                "restored_count": restored_count,
                "skipped_count": skipped_count,
                "success": True
            }

        except Exception as e:
            # Log restore failure
            await self.audit_repository.log_critical_operation(
                operation=AuditOperation.BACKUP_RESTORED,
                entity_type="coaching_relationship",
                message=f"Failed to restore from backup {backup_id}: {str(e)}",
                user_id=restore_user_id,
                error_message=str(e)
            )
            
            logger.error(f"❌ Error in restore_relationships_from_backup: {e}")
            raise

    async def get_available_backups(self, limit: int = 30) -> List[Dict[str, Any]]:
        """Get list of available backups"""
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                return []

            cursor = db[self.backup_collection].find(
                {"backup_type": "active_relationships"}
            ).sort("timestamp", -1).limit(limit)
            
            backups = await cursor.to_list(length=None)
            
            # Convert ObjectIds and format for response
            backup_list = []
            for backup in backups:
                backup_list.append({
                    "backup_id": str(backup["_id"]),
                    "timestamp": backup["timestamp"],
                    "relationship_count": backup.get("relationship_count", 0),
                    "environment": backup.get("environment", "unknown"),
                    "backup_version": backup.get("backup_version", "1.0")
                })
            
            return backup_list

        except Exception as e:
            logger.error(f"❌ Error getting available backups: {e}")
            return []

    async def cleanup_old_backups(self, retention_days: int = 30) -> int:
        """Clean up backups older than retention period"""
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                return 0

            cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
            
            result = await db[self.backup_collection].delete_many({
                "timestamp": {"$lt": cutoff_date}
            })

            deleted_count = result.deleted_count
            
            if deleted_count > 0:
                await self.audit_repository.log_operation(
                    operation=AuditOperation.BACKUP_CREATED,  # Using this for cleanup
                    severity=AuditSeverity.INFO,
                    entity_type="coaching_relationship",
                    message=f"Cleaned up {deleted_count} old backups (older than {retention_days} days)",
                    operation_details={
                        "deleted_count": deleted_count,
                        "retention_days": retention_days,
                        "cutoff_date": cutoff_date.isoformat()
                    },
                    tags=["backup", "cleanup"]
                )

            logger.info(f"🧹 Cleaned up {deleted_count} old backups")
            return deleted_count

        except Exception as e:
            logger.error(f"❌ Error cleaning up old backups: {e}")
            return 0

    async def verify_backup_integrity(self, backup_id: str) -> Dict[str, Any]:
        """Verify the integrity of a backup"""
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                return {"valid": False, "error": "Database connection failed"}

            backup_doc = await db[self.backup_collection].find_one({"_id": ObjectId(backup_id)})
            if not backup_doc:
                return {"valid": False, "error": "Backup not found"}

            relationships = backup_doc.get("relationships", [])
            issues = []

            # Check each relationship for required fields
            for i, rel in enumerate(relationships):
                if not rel.get("coach_user_id"):
                    issues.append(f"Relationship {i}: Missing coach_user_id")
                if not rel.get("client_user_id"):
                    issues.append(f"Relationship {i}: Missing client_user_id")
                if not rel.get("status"):
                    issues.append(f"Relationship {i}: Missing status")

            return {
                "valid": len(issues) == 0,
                "relationship_count": len(relationships),
                "issues": issues,
                "backup_timestamp": backup_doc.get("timestamp"),
                "environment": backup_doc.get("environment")
            }

        except Exception as e:
            logger.error(f"❌ Error verifying backup integrity: {e}")
            return {"valid": False, "error": str(e)}