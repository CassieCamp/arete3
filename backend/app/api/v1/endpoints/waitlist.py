from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from app.services.role_service import RoleService
from app.schemas.waitlist import (
    ApprovedUserCreate,
    ApprovedUserUpdate,
    ApprovedUserResponse,
    BulkImportRequest,
    BulkImportResponse,
    WaitlistStatsResponse,
    BackupResponse,
    RestoreRequest,
    RestoreResponse
)
from app.api.v1.deps import get_current_user
from app.models.user import User
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)
router = APIRouter()


def require_admin_role(current_user: User = Depends(get_current_user)) -> User:
    """Dependency to require admin role for protected endpoints"""
    # For now, we'll check if the user has admin role or is in a specific admin list
    # This can be enhanced later with proper admin role management
    if current_user.role not in ["admin", "coach"]:  # Temporary: allow coaches to manage waitlist
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


@router.get("/approved-users", response_model=List[ApprovedUserResponse])
async def get_approved_users(current_user: User = Depends(require_admin_role)):
    """Get all approved users"""
    try:
        logger.info(f"Admin {current_user.email} requesting all approved users")
        
        role_service = RoleService()
        approved_users = role_service.get_all_approved_users()
        
        # Convert to response format
        response_users = []
        for user in approved_users:
            try:
                # Parse datetime strings if they exist
                approved_at = user.get("approved_at")
                if isinstance(approved_at, str):
                    approved_at = datetime.fromisoformat(approved_at.replace('Z', '+00:00'))
                
                updated_at = user.get("updated_at")
                if isinstance(updated_at, str):
                    updated_at = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                
                response_user = ApprovedUserResponse(
                    email=user.get("email", ""),
                    role=user.get("role", "client"),
                    notes=user.get("notes", ""),
                    approved_at=approved_at or datetime.utcnow(),
                    approved_by=user.get("approved_by", "admin"),
                    status=user.get("status", "approved"),
                    updated_at=updated_at
                )
                response_users.append(response_user)
            except Exception as e:
                logger.warning(f"Error processing user {user.get('email', 'unknown')}: {e}")
                continue
        
        logger.info(f"Returning {len(response_users)} approved users")
        return response_users
        
    except Exception as e:
        logger.error(f"Error getting approved users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve approved users"
        )


@router.post("/approved-users", response_model=ApprovedUserResponse)
async def add_approved_user(
    user_data: ApprovedUserCreate,
    current_user: User = Depends(require_admin_role)
):
    """Add a new approved user"""
    try:
        logger.info(f"Admin {current_user.email} adding approved user: {user_data.email}")
        
        role_service = RoleService()
        
        # Use the current user's email as approved_by if not specified
        approved_by = user_data.approved_by or current_user.email
        
        success = role_service.add_approved_user(
            email=user_data.email,
            role=user_data.role,
            approved_by=approved_by,
            notes=user_data.notes
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to add approved user. User may already exist."
            )
        
        # Get the newly added user to return
        added_user = role_service.get_approved_user(user_data.email)
        if not added_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User was added but could not be retrieved"
            )
        
        # Convert to response format
        approved_at = added_user.get("approved_at")
        if isinstance(approved_at, str):
            approved_at = datetime.fromisoformat(approved_at.replace('Z', '+00:00'))
        
        response = ApprovedUserResponse(
            email=added_user["email"],
            role=added_user["role"],
            notes=added_user.get("notes", ""),
            approved_at=approved_at or datetime.utcnow(),
            approved_by=added_user.get("approved_by", approved_by),
            status=added_user.get("status", "approved")
        )
        
        logger.info(f"Successfully added approved user: {user_data.email}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding approved user {user_data.email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add approved user"
        )


@router.put("/approved-users/{email}", response_model=ApprovedUserResponse)
async def update_approved_user(
    email: str,
    update_data: ApprovedUserUpdate,
    current_user: User = Depends(require_admin_role)
):
    """Update an approved user"""
    try:
        logger.info(f"Admin {current_user.email} updating approved user: {email}")
        
        role_service = RoleService()
        
        # Check if user exists
        existing_user = role_service.get_approved_user(email)
        if not existing_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Approved user not found"
            )
        
        # Prepare updates
        updates = {}
        if update_data.role is not None:
            updates["role"] = update_data.role
        if update_data.notes is not None:
            updates["notes"] = update_data.notes
        if update_data.status is not None:
            updates["status"] = update_data.status
        if update_data.approved_by is not None:
            updates["approved_by"] = update_data.approved_by
        
        # Add who made the update
        updates["updated_by"] = current_user.email
        
        success = role_service.update_approved_user(email, updates)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update approved user"
            )
        
        # Get the updated user to return
        updated_user = role_service.get_approved_user(email)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User was updated but could not be retrieved"
            )
        
        # Convert to response format
        approved_at = updated_user.get("approved_at")
        if isinstance(approved_at, str):
            approved_at = datetime.fromisoformat(approved_at.replace('Z', '+00:00'))
        
        updated_at = updated_user.get("updated_at")
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
        
        response = ApprovedUserResponse(
            email=updated_user["email"],
            role=updated_user["role"],
            notes=updated_user.get("notes", ""),
            approved_at=approved_at or datetime.utcnow(),
            approved_by=updated_user.get("approved_by", "admin"),
            status=updated_user.get("status", "approved"),
            updated_at=updated_at
        )
        
        logger.info(f"Successfully updated approved user: {email}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating approved user {email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update approved user"
        )


@router.delete("/approved-users/{email}")
async def remove_approved_user(
    email: str,
    current_user: User = Depends(require_admin_role)
):
    """Remove an approved user"""
    try:
        logger.info(f"Admin {current_user.email} removing approved user: {email}")
        
        role_service = RoleService()
        
        # Check if user exists
        existing_user = role_service.get_approved_user(email)
        if not existing_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Approved user not found"
            )
        
        success = role_service.remove_approved_user(email)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to remove approved user"
            )
        
        logger.info(f"Successfully removed approved user: {email}")
        return {"message": f"Approved user {email} removed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing approved user {email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove approved user"
        )


@router.post("/approved-users/bulk", response_model=BulkImportResponse)
async def bulk_import_users(
    import_data: BulkImportRequest,
    current_user: User = Depends(require_admin_role)
):
    """Bulk import approved users"""
    try:
        logger.info(f"Admin {current_user.email} bulk importing {len(import_data.users)} users")
        
        role_service = RoleService()
        
        # Convert to the format expected by role service
        users_to_import = []
        for user in import_data.users:
            users_to_import.append({
                "email": user.email,
                "role": user.role,
                "notes": user.notes
            })
        
        # Use the current user's email as approved_by if not specified
        approved_by = import_data.approved_by or current_user.email
        
        results = role_service.bulk_import_users(users_to_import, approved_by)
        
        response = BulkImportResponse(
            success=results["success"],
            failed=results["failed"],
            errors=results["errors"]
        )
        
        logger.info(f"Bulk import completed: {results['success']} success, {results['failed']} failed")
        return response
        
    except Exception as e:
        logger.error(f"Error in bulk import: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to bulk import users"
        )


@router.get("/stats", response_model=WaitlistStatsResponse)
async def get_waitlist_stats(current_user: User = Depends(require_admin_role)):
    """Get waitlist statistics"""
    try:
        logger.info(f"Admin {current_user.email} requesting waitlist stats")
        
        role_service = RoleService()
        approved_users = role_service.get_all_approved_users()
        
        total_approved = len(approved_users)
        coaches = len([u for u in approved_users if u.get("role") == "coach"])
        clients = len([u for u in approved_users if u.get("role") == "client"])
        
        # Count recent approvals (last 7 days)
        recent_approvals = 0
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        
        for user in approved_users:
            approved_at = user.get("approved_at")
            if approved_at:
                try:
                    if isinstance(approved_at, str):
                        approved_at = datetime.fromisoformat(approved_at.replace('Z', '+00:00'))
                    if approved_at >= seven_days_ago:
                        recent_approvals += 1
                except Exception:
                    continue
        
        response = WaitlistStatsResponse(
            total_approved=total_approved,
            coaches=coaches,
            clients=clients,
            recent_approvals=recent_approvals
        )
        
        logger.info(f"Waitlist stats: {total_approved} total, {coaches} coaches, {clients} clients")
        return response
        
    except Exception as e:
        logger.error(f"Error getting waitlist stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve waitlist statistics"
        )


@router.post("/backup", response_model=BackupResponse)
async def create_backup(current_user: User = Depends(require_admin_role)):
    """Create a backup of the approved users configuration"""
    try:
        logger.info(f"Admin {current_user.email} creating backup")
        
        role_service = RoleService()
        backup_path = role_service._create_backup()
        
        if backup_path:
            response = BackupResponse(
                success=True,
                backup_path=backup_path,
                message="Backup created successfully"
            )
        else:
            response = BackupResponse(
                success=False,
                message="Failed to create backup"
            )
        
        logger.info(f"Backup creation result: {response.success}")
        return response
        
    except Exception as e:
        logger.error(f"Error creating backup: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create backup"
        )


@router.post("/restore", response_model=RestoreResponse)
async def restore_from_backup(
    restore_data: RestoreRequest,
    current_user: User = Depends(require_admin_role)
):
    """Restore approved users from a backup"""
    try:
        logger.info(f"Admin {current_user.email} restoring from backup: {restore_data.backup_path}")
        
        role_service = RoleService()
        success = role_service.restore_from_backup(restore_data.backup_path)
        
        if success:
            # Count restored users
            approved_users = role_service.get_all_approved_users()
            users_restored = len(approved_users)
            
            response = RestoreResponse(
                success=True,
                message="Backup restored successfully",
                users_restored=users_restored
            )
        else:
            response = RestoreResponse(
                success=False,
                message="Failed to restore from backup"
            )
        
        logger.info(f"Restore result: {response.success}")
        return response
        
    except Exception as e:
        logger.error(f"Error restoring from backup: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to restore from backup"
        )