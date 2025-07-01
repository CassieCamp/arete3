from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from bson import ObjectId
from app.models.coaching_relationship import CoachingRelationship, RelationshipStatus
from app.models.audit_log import AuditOperation, AuditSeverity
from app.repositories.audit_repository import AuditRepository
from app.db.mongodb import get_database
import logging
import asyncio

logger = logging.getLogger(__name__)


class RelationshipMonitoringService:
    """
    Service for monitoring relationship integrity and detecting anomalies
    """
    
    def __init__(self):
        self.audit_repository = AuditRepository()
        self.last_known_count = None
        self.monitoring_active = False

    async def start_monitoring(self):
        """Start the relationship monitoring service"""
        logger.info("🔍 Starting relationship monitoring service")
        self.monitoring_active = True
        
        # Initialize baseline count
        await self.update_baseline_count()
        
        # Start monitoring loop (in production, this would be a background task)
        logger.info("✅ Relationship monitoring service started")

    async def stop_monitoring(self):
        """Stop the relationship monitoring service"""
        logger.info("🛑 Stopping relationship monitoring service")
        self.monitoring_active = False

    async def update_baseline_count(self) -> int:
        """Update the baseline count of active relationships"""
        try:
            current_count = await self.count_active_relationships()
            self.last_known_count = current_count
            logger.info(f"📊 Updated baseline relationship count: {current_count}")
            return current_count
        except Exception as e:
            logger.error(f"❌ Error updating baseline count: {e}")
            return 0

    async def count_active_relationships(self) -> int:
        """Count all active (non-deleted) relationships"""
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                return 0

            count = await db["coaching_relationships"].count_documents({
                "$and": [
                    {"status": {"$ne": "deleted"}},
                    {"deleted_at": {"$exists": False}}
                ]
            })
            
            return count

        except Exception as e:
            logger.error(f"❌ Error counting active relationships: {e}")
            return 0

    async def detect_mass_deletion(self, threshold: int = 5) -> Dict[str, Any]:
        """Detect if there's been a mass deletion of relationships"""
        try:
            current_count = await self.count_active_relationships()
            
            if self.last_known_count is None:
                self.last_known_count = current_count
                return {"mass_deletion_detected": False, "current_count": current_count}

            count_drop = self.last_known_count - current_count
            
            if count_drop >= threshold:
                # Mass deletion detected!
                await self.audit_repository.log_critical_operation(
                    operation=AuditOperation.MASS_DELETE_DETECTED,
                    entity_type="coaching_relationship",
                    message=f"🚨 MASS DELETION DETECTED: {count_drop} relationships lost (from {self.last_known_count} to {current_count})",
                    operation_details={
                        "previous_count": self.last_known_count,
                        "current_count": current_count,
                        "relationships_lost": count_drop,
                        "threshold": threshold
                    }
                )
                
                logger.critical(f"🚨 MASS DELETION DETECTED: {count_drop} relationships lost!")
                
                return {
                    "mass_deletion_detected": True,
                    "previous_count": self.last_known_count,
                    "current_count": current_count,
                    "relationships_lost": count_drop,
                    "severity": "critical"
                }
            
            # Update baseline if count increased or small decrease
            if count_drop < threshold:
                self.last_known_count = current_count
            
            return {
                "mass_deletion_detected": False,
                "current_count": current_count,
                "previous_count": self.last_known_count,
                "change": current_count - self.last_known_count
            }

        except Exception as e:
            logger.error(f"❌ Error detecting mass deletion: {e}")
            return {"mass_deletion_detected": False, "error": str(e)}

    async def verify_relationship_integrity(self) -> Dict[str, Any]:
        """Verify the integrity of all relationships"""
        logger.info("🔍 Starting relationship integrity verification")
        
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                return {"integrity_check_passed": False, "error": "Database connection failed"}

            issues = []
            
            # Get all relationships
            cursor = db["coaching_relationships"].find({})
            relationships = await cursor.to_list(length=None)
            
            for rel in relationships:
                rel_id = str(rel.get("_id", "unknown"))
                
                # Check for orphaned relationships (users don't exist)
                coach_exists = await self._user_exists(rel.get("coach_user_id"))
                client_exists = await self._user_exists(rel.get("client_user_id"))
                
                if not coach_exists:
                    issues.append({
                        "type": "orphaned_coach",
                        "relationship_id": rel_id,
                        "coach_user_id": rel.get("coach_user_id"),
                        "message": f"Coach user {rel.get('coach_user_id')} not found"
                    })
                
                if not client_exists:
                    issues.append({
                        "type": "orphaned_client",
                        "relationship_id": rel_id,
                        "client_user_id": rel.get("client_user_id"),
                        "message": f"Client user {rel.get('client_user_id')} not found"
                    })
                
                # Check for inconsistent soft delete state
                status = rel.get("status")
                deleted_at = rel.get("deleted_at")
                
                if status == "deleted" and not deleted_at:
                    issues.append({
                        "type": "inconsistent_soft_delete",
                        "relationship_id": rel_id,
                        "message": "Status is 'deleted' but deleted_at is not set"
                    })
                
                if deleted_at and status != "deleted":
                    issues.append({
                        "type": "inconsistent_soft_delete",
                        "relationship_id": rel_id,
                        "message": "deleted_at is set but status is not 'deleted'"
                    })

            # Check for orphaned session insights
            orphaned_insights = await self._find_orphaned_session_insights()
            for insight in orphaned_insights:
                issues.append({
                    "type": "orphaned_session_insight",
                    "insight_id": insight["insight_id"],
                    "relationship_id": insight["relationship_id"],
                    "message": f"Session insight exists but relationship {insight['relationship_id']} not found"
                })

            # Log results
            if issues:
                await self.audit_repository.log_critical_operation(
                    operation=AuditOperation.INTEGRITY_CHECK_FAILED,
                    entity_type="coaching_relationship",
                    message=f"Integrity check found {len(issues)} issues",
                    operation_details={
                        "total_relationships": len(relationships),
                        "issues_found": len(issues),
                        "issue_types": list(set(issue["type"] for issue in issues))
                    }
                )
                logger.warning(f"⚠️ Integrity check found {len(issues)} issues")
            else:
                logger.info("✅ Relationship integrity check passed")

            return {
                "integrity_check_passed": len(issues) == 0,
                "total_relationships": len(relationships),
                "issues_found": len(issues),
                "issues": issues,
                "timestamp": datetime.utcnow()
            }

        except Exception as e:
            logger.error(f"❌ Error in relationship integrity verification: {e}")
            return {"integrity_check_passed": False, "error": str(e)}

    async def _user_exists(self, user_id: str) -> bool:
        """Check if a user exists in the database"""
        try:
            if not user_id:
                return False
                
            db = get_database()
            if db is None:
                return False

            user = await db["users"].find_one({"clerk_user_id": user_id})
            return user is not None

        except Exception as e:
            logger.error(f"❌ Error checking if user exists: {e}")
            return False

    async def _find_orphaned_session_insights(self) -> List[Dict[str, Any]]:
        """Find session insights that reference non-existent relationships"""
        try:
            db = get_database()
            if db is None:
                return []

            # Get all session insights
            cursor = db["session_insights"].find({})
            insights = await cursor.to_list(length=None)
            
            orphaned = []
            
            for insight in insights:
                relationship_id = insight.get("coaching_relationship_id")
                if not relationship_id:
                    continue
                
                # Check if relationship exists
                relationship = await db["coaching_relationships"].find_one({"_id": ObjectId(relationship_id)})
                if not relationship:
                    orphaned.append({
                        "insight_id": str(insight.get("_id")),
                        "relationship_id": relationship_id,
                        "coach_user_id": insight.get("coach_user_id"),
                        "client_user_id": insight.get("client_user_id")
                    })
            
            return orphaned

        except Exception as e:
            logger.error(f"❌ Error finding orphaned session insights: {e}")
            return []

    async def auto_restore_lost_relationships(self) -> Dict[str, Any]:
        """Attempt to auto-restore relationships based on session insights"""
        logger.info("🔄 Starting auto-restore of lost relationships")
        
        try:
            orphaned_insights = await self._find_orphaned_session_insights()
            
            if not orphaned_insights:
                logger.info("✅ No orphaned session insights found")
                return {"restored_count": 0, "message": "No relationships to restore"}

            restored_count = 0
            failed_count = 0
            
            # Group insights by coach-client pairs
            relationship_pairs = {}
            for insight in orphaned_insights:
                coach_id = insight["coach_user_id"]
                client_id = insight["client_user_id"]
                pair_key = f"{coach_id}:{client_id}"
                
                if pair_key not in relationship_pairs:
                    relationship_pairs[pair_key] = {
                        "coach_user_id": coach_id,
                        "client_user_id": client_id,
                        "insight_count": 0
                    }
                relationship_pairs[pair_key]["insight_count"] += 1

            # Attempt to restore each relationship
            db = get_database()
            for pair_key, pair_data in relationship_pairs.items():
                try:
                    # Verify both users still exist
                    coach_exists = await self._user_exists(pair_data["coach_user_id"])
                    client_exists = await self._user_exists(pair_data["client_user_id"])
                    
                    if not coach_exists or not client_exists:
                        failed_count += 1
                        continue
                    
                    # Check if relationship already exists
                    existing = await db["coaching_relationships"].find_one({
                        "coach_user_id": pair_data["coach_user_id"],
                        "client_user_id": pair_data["client_user_id"]
                    })
                    
                    if existing:
                        continue  # Already exists
                    
                    # Create new relationship
                    new_relationship = {
                        "coach_user_id": pair_data["coach_user_id"],
                        "client_user_id": pair_data["client_user_id"],
                        "status": RelationshipStatus.ACTIVE.value,
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                    
                    result = await db["coaching_relationships"].insert_one(new_relationship)
                    
                    # Log the restoration
                    await self.audit_repository.log_critical_operation(
                        operation=AuditOperation.RESTORE_RELATIONSHIP,
                        entity_type="coaching_relationship",
                        entity_id=str(result.inserted_id),
                        message=f"Auto-restored relationship based on {pair_data['insight_count']} session insights",
                        operation_details={
                            "coach_user_id": pair_data["coach_user_id"],
                            "client_user_id": pair_data["client_user_id"],
                            "insight_count": pair_data["insight_count"],
                            "restoration_method": "auto_restore_from_insights"
                        }
                    )
                    
                    restored_count += 1
                    logger.info(f"✅ Auto-restored relationship for {pair_key}")
                    
                except Exception as rel_error:
                    logger.error(f"❌ Failed to restore relationship {pair_key}: {rel_error}")
                    failed_count += 1

            logger.info(f"🔄 Auto-restore completed: {restored_count} restored, {failed_count} failed")
            
            return {
                "restored_count": restored_count,
                "failed_count": failed_count,
                "total_orphaned_insights": len(orphaned_insights),
                "unique_relationships": len(relationship_pairs)
            }

        except Exception as e:
            logger.error(f"❌ Error in auto_restore_lost_relationships: {e}")
            return {"restored_count": 0, "error": str(e)}

    async def get_monitoring_status(self) -> Dict[str, Any]:
        """Get current monitoring status and statistics"""
        try:
            current_count = await self.count_active_relationships()
            
            return {
                "monitoring_active": self.monitoring_active,
                "current_relationship_count": current_count,
                "last_known_count": self.last_known_count,
                "last_check_time": datetime.utcnow(),
                "status": "healthy" if self.monitoring_active else "inactive"
            }

        except Exception as e:
            logger.error(f"❌ Error getting monitoring status: {e}")
            return {"status": "error", "error": str(e)}