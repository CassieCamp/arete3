from fastapi import APIRouter, Depends, HTTPException, status
from app.api.v1.deps import get_current_user_clerk_id
from app.services.user_service import UserService
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/me/roles")
async def get_current_user_roles(
    clerk_user_id: str = Depends(get_current_user_clerk_id)
) -> Dict[str, Any]:
    """
    Get current user's organization roles and permissions.
    
    Returns comprehensive role information including:
    - Primary role
    - Organization roles with permissions
    - All available permissions
    """
    try:
        logger.info(f"Getting roles for user: {clerk_user_id}")
        
        user_service = UserService()
        roles_data = await user_service.get_user_roles(clerk_user_id)
        
        if not roles_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Format the response according to the frontend expectations
        response = {
            "user_id": roles_data["user_id"],
            "clerk_user_id": roles_data["clerk_user_id"],
            "email": roles_data["email"],
            "primaryRole": roles_data["primary_role"],
            "roles": roles_data.get("roles", []),
            "organizationRoles": roles_data.get("organization_roles", []),
            "organizationMemberships": roles_data.get("organization_memberships", []),
            "permissions": roles_data.get("permissions", [])
        }
        
        logger.info(f"✅ Successfully retrieved roles for user {clerk_user_id}")
        logger.info(f"Primary role: {response['primaryRole']}")
        logger.info(f"Organization roles count: {len(response['organizationRoles'])}")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting user roles for {clerk_user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user roles"
        )


@router.get("/me/permissions")
async def get_current_user_permissions(
    clerk_user_id: str = Depends(get_current_user_clerk_id)
) -> Dict[str, Any]:
    """
    Get current user's permissions only.
    
    Returns just the permissions array for quick permission checks.
    """
    try:
        logger.info(f"Getting permissions for user: {clerk_user_id}")
        
        user_service = UserService()
        roles_data = await user_service.get_user_roles(clerk_user_id)
        
        if not roles_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {
            "permissions": roles_data.get("permissions", []),
            "primaryRole": roles_data["primary_role"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting user permissions for {clerk_user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user permissions"
        )


@router.get("/me/organizations")
async def get_current_user_organizations(
    clerk_user_id: str = Depends(get_current_user_clerk_id)
) -> Dict[str, Any]:
    """
    Get current user's organization memberships.
    
    Returns organization memberships and roles.
    """
    try:
        logger.info(f"Getting organizations for user: {clerk_user_id}")
        
        user_service = UserService()
        roles_data = await user_service.get_user_roles(clerk_user_id)
        
        if not roles_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {
            "organizationMemberships": roles_data.get("organization_memberships", []),
            "organizationRoles": roles_data.get("organization_roles", [])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting user organizations for {clerk_user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user organizations"
        )