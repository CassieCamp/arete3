# DEPRECATED: This schema is no longer in use and will be removed in a future update.
# The functionality has been replaced by the coaching_interest schema and related services.

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime


class ApprovedUserBase(BaseModel):
    """Base schema for approved user data"""
    email: EmailStr
    role: str = Field(..., pattern="^(coach|client)$", description="User role: coach or client")
    notes: Optional[str] = Field(default="", description="Optional notes about the approval")


class ApprovedUserCreate(ApprovedUserBase):
    """Schema for creating a new approved user"""
    approved_by: Optional[str] = Field(default="admin", description="Who approved this user")


class ApprovedUserUpdate(BaseModel):
    """Schema for updating an approved user"""
    role: Optional[str] = Field(None, pattern="^(coach|client)$", description="User role: coach or client")
    notes: Optional[str] = Field(None, description="Optional notes about the approval")
    status: Optional[str] = Field(None, pattern="^(approved|pending|rejected)$", description="Approval status")
    approved_by: Optional[str] = Field(None, description="Who approved this user")


class ApprovedUserResponse(ApprovedUserBase):
    """Schema for approved user response"""
    approved_at: datetime = Field(..., description="When the user was approved")
    approved_by: str = Field(..., description="Who approved this user")
    status: str = Field(default="approved", description="Approval status")
    updated_at: Optional[datetime] = Field(None, description="When the user was last updated")

    class Config:
        from_attributes = True


class BulkImportRequest(BaseModel):
    """Schema for bulk import request"""
    users: List[ApprovedUserBase] = Field(..., description="List of users to import")
    approved_by: Optional[str] = Field(default="admin", description="Who approved these users")


class BulkImportResponse(BaseModel):
    """Schema for bulk import response"""
    success: int = Field(..., description="Number of successfully imported users")
    failed: int = Field(..., description="Number of failed imports")
    errors: List[str] = Field(default_factory=list, description="List of error messages")


class WaitlistStatsResponse(BaseModel):
    """Schema for waitlist statistics"""
    total_approved: int = Field(..., description="Total number of approved users")
    coaches: int = Field(..., description="Number of approved coaches")
    clients: int = Field(..., description="Number of approved clients")
    recent_approvals: int = Field(..., description="Number of approvals in the last 7 days")


class BackupResponse(BaseModel):
    """Schema for backup operation response"""
    success: bool = Field(..., description="Whether the backup was successful")
    backup_path: Optional[str] = Field(None, description="Path to the backup file")
    message: str = Field(..., description="Status message")


class RestoreRequest(BaseModel):
    """Schema for restore operation request"""
    backup_path: str = Field(..., description="Path to the backup file to restore from")


class RestoreResponse(BaseModel):
    """Schema for restore operation response"""
    success: bool = Field(..., description="Whether the restore was successful")
    message: str = Field(..., description="Status message")
    users_restored: Optional[int] = Field(None, description="Number of users restored")