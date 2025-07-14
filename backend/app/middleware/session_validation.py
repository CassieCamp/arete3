"""
Session Validation Middleware

Detects stale JWT claims and provides session refresh recommendations
when Clerk publicMetadata doesn't match JWT claims.
"""

import logging
from typing import Dict, Any, Optional
from fastapi import Request, HTTPException, status
from app.core.config import settings
from clerk_backend_api import Clerk

logger = logging.getLogger(__name__)

class SessionValidationMiddleware:
    """Middleware to validate JWT claims against Clerk publicMetadata"""
    
    def __init__(self):
        self.clerk_client = Clerk(bearer_auth=settings.clerk_secret_key)
    
    async def validate_session_freshness(self, 
                                       clerk_user_id: str, 
                                       jwt_claims: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate that JWT claims match current Clerk publicMetadata
        
        Returns validation result with recommendations
        """
        try:
            # Get current user data from Clerk
            clerk_user = self.clerk_client.users.get(user_id=clerk_user_id)
            current_metadata = clerk_user.public_metadata or {}
            
            # Extract role information
            current_primary_role = current_metadata.get("primary_role", "member")
            current_org_roles = current_metadata.get("organization_roles", {})
            
            # Extract JWT claims
            jwt_metadata = jwt_claims.get("publicMetadata", {})
            jwt_primary_role = jwt_metadata.get("primary_role", "member")
            jwt_org_roles = jwt_metadata.get("organization_roles", {})
            
            # Check for mismatches
            role_mismatch = current_primary_role != jwt_primary_role
            org_roles_mismatch = current_org_roles != jwt_org_roles
            
            validation_result = {
                "is_fresh": not (role_mismatch or org_roles_mismatch),
                "clerk_primary_role": current_primary_role,
                "jwt_primary_role": jwt_primary_role,
                "clerk_org_roles": current_org_roles,
                "jwt_org_roles": jwt_org_roles,
                "role_mismatch": role_mismatch,
                "org_roles_mismatch": org_roles_mismatch,
                "refresh_recommended": role_mismatch or org_roles_mismatch
            }
            
            if validation_result["refresh_recommended"]:
                logger.warning(
                    f"🔄 Stale session detected for user {clerk_user_id}: "
                    f"Clerk role='{current_primary_role}', JWT role='{jwt_primary_role}'"
                )
            else:
                logger.debug(f"✅ Session is fresh for user {clerk_user_id}")
            
            return validation_result
            
        except Exception as e:
            logger.error(f"❌ Error validating session freshness for {clerk_user_id}: {e}")
            return {
                "is_fresh": True,  # Assume fresh on error to avoid blocking
                "error": str(e),
                "refresh_recommended": False
            }
    
    async def add_session_headers(self, 
                                response_headers: Dict[str, str], 
                                validation_result: Dict[str, Any]) -> None:
        """Add session validation headers to response"""
        
        if validation_result.get("refresh_recommended"):
            response_headers["X-Session-Refresh-Recommended"] = "true"
            response_headers["X-Session-Stale-Reason"] = "role-mismatch"
            
            if validation_result.get("role_mismatch"):
                response_headers["X-Expected-Role"] = validation_result.get("clerk_primary_role", "")
                response_headers["X-Current-JWT-Role"] = validation_result.get("jwt_primary_role", "")
        else:
            response_headers["X-Session-Fresh"] = "true"
    
    async def handle_stale_session(self, 
                                 clerk_user_id: str, 
                                 validation_result: Dict[str, Any],
                                 strict_mode: bool = False) -> Optional[HTTPException]:
        """
        Handle stale session detection
        
        Args:
            clerk_user_id: The user's Clerk ID
            validation_result: Result from validate_session_freshness
            strict_mode: If True, raise exception for stale sessions
        
        Returns:
            HTTPException if strict_mode is True and session is stale, None otherwise
        """
        
        if not validation_result.get("refresh_recommended"):
            return None
        
        if strict_mode:
            logger.warning(f"🚫 Blocking stale session for user {clerk_user_id} (strict mode)")
            return HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session is stale, please refresh your session",
                headers={
                    "X-Session-Refresh-Required": "true",
                    "X-Session-Stale-Reason": "role-mismatch"
                }
            )
        else:
            # Log warning but allow request to proceed
            logger.warning(
                f"⚠️ Allowing stale session for user {clerk_user_id} "
                f"(role mismatch: Clerk='{validation_result.get('clerk_primary_role')}', "
                f"JWT='{validation_result.get('jwt_primary_role')}')"
            )
            return None


# Global middleware instance
session_validator = SessionValidationMiddleware()


async def validate_user_session(request: Request, 
                               clerk_user_id: str, 
                               jwt_claims: Dict[str, Any],
                               strict_mode: bool = False) -> Dict[str, Any]:
    """
    Convenience function to validate user session
    
    Args:
        request: FastAPI request object
        clerk_user_id: User's Clerk ID
        jwt_claims: Decoded JWT claims
        strict_mode: Whether to enforce strict session validation
    
    Returns:
        Validation result dictionary
    """
    
    validation_result = await session_validator.validate_session_freshness(
        clerk_user_id, jwt_claims
    )
    
    # Handle stale session if needed
    exception = await session_validator.handle_stale_session(
        clerk_user_id, validation_result, strict_mode
    )
    
    if exception:
        raise exception
    
    return validation_result


def add_session_validation_headers(response_headers: Dict[str, str], 
                                 validation_result: Dict[str, Any]) -> None:
    """Add session validation headers to response"""
    session_validator.add_session_headers(response_headers, validation_result)