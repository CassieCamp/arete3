from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from bson import ObjectId
from app.models.audit_log import AuditLog, AuditOperation, AuditSeverity
from app.db.mongodb import get_database
import logging
import traceback
import os

logger = logging.getLogger(__name__)


class AuditRepository:
    def __init__(self):
        self.collection_name = "audit_logs"

    async def log_operation(
        self,
        operation: AuditOperation,
        severity: AuditSeverity,
        entity_type: str,
        message: str,
        entity_id: Optional[str] = None,
        user_id: Optional[str] = None,
        operation_details: Optional[Dict[str, Any]] = None,
        before_state: Optional[Dict[str, Any]] = None,
        after_state: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        include_stack_trace: bool = False,
        tags: Optional[List[str]] = None
    ) -> AuditLog:
        """Log an audit operation"""
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                raise Exception("Database connection is None")

            # Create audit log entry
            audit_log = AuditLog(
                operation=operation,
                severity=severity,
                entity_type=entity_type,
                entity_id=entity_id,
                user_id=user_id,
                operation_details=operation_details or {},
                before_state=before_state,
                after_state=after_state,
                message=message,
                error_message=error_message,
                stack_trace=traceback.format_stack() if include_stack_trace else None,
                environment=os.getenv("ENVIRONMENT", "development"),
                tags=tags or [],
                timestamp=datetime.utcnow()
            )

            # Set expiration for log retention (90 days for critical, 30 days for others)
            if severity == AuditSeverity.CRITICAL or severity == AuditSeverity.EMERGENCY:
                audit_log.expires_at = datetime.utcnow() + timedelta(days=90)
            else:
                audit_log.expires_at = datetime.utcnow() + timedelta(days=30)

            # Convert to dict and insert
            audit_dict = audit_log.dict(by_alias=True, exclude_unset=True)
            if "_id" in audit_dict and audit_dict["_id"] is None:
                del audit_dict["_id"]

            result = await db[self.collection_name].insert_one(audit_dict)
            audit_log.id = result.inserted_id

            # Log to application logger as well for immediate visibility
            log_level = {
                AuditSeverity.INFO: logging.INFO,
                AuditSeverity.WARNING: logging.WARNING,
                AuditSeverity.CRITICAL: logging.CRITICAL,
                AuditSeverity.EMERGENCY: logging.CRITICAL
            }.get(severity, logging.INFO)
            
            logger.log(log_level, f"🔍 AUDIT: {operation.value} - {message}")

            return audit_log

        except Exception as e:
            logger.error(f"❌ Failed to log audit operation: {e}")
            # Don't raise exception to avoid breaking the main operation
            return None

    async def log_critical_operation(
        self,
        operation: AuditOperation,
        entity_type: str,
        message: str,
        entity_id: Optional[str] = None,
        user_id: Optional[str] = None,
        operation_details: Optional[Dict[str, Any]] = None,
        before_state: Optional[Dict[str, Any]] = None,
        after_state: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None
    ) -> AuditLog:
        """Log a critical operation with stack trace"""
        return await self.log_operation(
            operation=operation,
            severity=AuditSeverity.CRITICAL,
            entity_type=entity_type,
            message=message,
            entity_id=entity_id,
            user_id=user_id,
            operation_details=operation_details,
            before_state=before_state,
            after_state=after_state,
            error_message=error_message,
            include_stack_trace=True,
            tags=["critical", "requires_investigation"]
        )

    async def get_audit_logs(
        self,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        operation: Optional[AuditOperation] = None,
        severity: Optional[AuditSeverity] = None,
        user_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[AuditLog]:
        """Retrieve audit logs with filtering"""
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                return []

            # Build query
            query = {}
            if entity_type:
                query["entity_type"] = entity_type
            if entity_id:
                query["entity_id"] = entity_id
            if operation:
                query["operation"] = operation.value
            if severity:
                query["severity"] = severity.value
            if user_id:
                query["user_id"] = user_id
            if start_date or end_date:
                date_query = {}
                if start_date:
                    date_query["$gte"] = start_date
                if end_date:
                    date_query["$lte"] = end_date
                query["timestamp"] = date_query

            # Execute query
            cursor = db[self.collection_name].find(query).sort("timestamp", -1).limit(limit)
            audit_docs = await cursor.to_list(length=None)

            # Convert to models
            audit_logs = []
            for doc in audit_docs:
                if "_id" in doc and doc["_id"]:
                    doc["_id"] = str(doc["_id"])
                audit_logs.append(AuditLog(**doc))

            return audit_logs

        except Exception as e:
            logger.error(f"❌ Error retrieving audit logs: {e}")
            return []

    async def get_critical_alerts(self, hours: int = 24) -> List[AuditLog]:
        """Get critical audit logs from the last N hours"""
        start_date = datetime.utcnow() - timedelta(hours=hours)
        return await self.get_audit_logs(
            severity=AuditSeverity.CRITICAL,
            start_date=start_date,
            limit=50
        )

    async def cleanup_expired_logs(self) -> int:
        """Clean up expired audit logs"""
        try:
            db = get_database()
            if db is None:
                logger.error("Database is None")
                return 0

            result = await db[self.collection_name].delete_many({
                "expires_at": {"$lt": datetime.utcnow()}
            })

            logger.info(f"🧹 Cleaned up {result.deleted_count} expired audit logs")
            return result.deleted_count

        except Exception as e:
            logger.error(f"❌ Error cleaning up audit logs: {e}")
            return 0