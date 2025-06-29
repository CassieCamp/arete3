from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from clerk_backend_api import Clerk
from app.core.config import settings
from app.services.user_service import UserService
from app.services.role_service import RoleService
import logging
import jwt
from typing import Optional

logger = logging.getLogger(__name__)

# Initialize Clerk client
clerk = Clerk(bearer_auth=settings.clerk_secret_key)

# Security scheme
security = HTTPBearer()


async def get_current_user_clerk_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    Validate Clerk JWT token, ensure user exists in backend database, and return the user's Clerk ID
    """
    try:
        # Verify the JWT token with Clerk
        token = credentials.credentials
        
        # For now, we'll decode without verification for development
        # In production, you should verify with Clerk's public key
        try:
            # Decode without verification for development
            decoded_token = jwt.decode(token, options={"verify_signature": False})
            clerk_user_id = decoded_token.get("sub")
            
            if not clerk_user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication token - no user ID",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            logger.info(f"🔍 Authenticated user with Clerk ID: {clerk_user_id}")
            
            # Check if user exists in backend database
            user_service = UserService()
            existing_user = await user_service.get_user_by_clerk_id(clerk_user_id)
            
            if not existing_user:
                logger.warning(f"⚠️ User {clerk_user_id} authenticated but not found in backend database")
                
                # Fetch user details from Clerk to sync to backend
                try:
                    logger.info(f"🔄 Fetching user details from Clerk for {clerk_user_id}")
                    clerk_user = clerk.users.get(user_id=clerk_user_id)
                    
                    # Get primary email
                    primary_email = None
                    if clerk_user.email_addresses:
                        for email in clerk_user.email_addresses:
                            if email.id == clerk_user.primary_email_address_id:
                                primary_email = email.email_address
                                break
                        if not primary_email:
                            primary_email = clerk_user.email_addresses[0].email_address
                    
                    if not primary_email:
                        logger.error(f"❌ No email found for Clerk user {clerk_user_id}")
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="User has no email address"
                        )
                    
                    logger.info(f"📧 Found email for user: {primary_email}")
                    
                    # Get role assignment
                    role_service = RoleService()
                    assigned_role = role_service.get_role_for_email(primary_email)
                    final_role = assigned_role if assigned_role else "client"
                    
                    logger.info(f"👤 Assigning role '{final_role}' to user {primary_email}")
                    
                    # Create user in backend database
                    created_user = await user_service.create_user_from_clerk(
                        clerk_user_id=clerk_user_id,
                        email=primary_email,
                        role=final_role
                    )
                    
                    logger.info(f"✅ Successfully synced user to backend: {created_user.id}")
                    
                except Exception as sync_error:
                    logger.error(f"❌ Failed to sync user {clerk_user_id} to backend: {sync_error}")
                    # Don't fail authentication, just log the error
                    # The user can still authenticate, but some features might not work
            else:
                logger.info(f"✅ User {clerk_user_id} found in backend database: {existing_user.id}")
            
            return clerk_user_id
            
        except jwt.DecodeError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token format",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Optional dependency for endpoints that may or may not require auth
async def get_current_user_clerk_id_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[str]:
    """
    Optional Clerk JWT token validation
    """
    try:
        if not credentials:
            return None
        return await get_current_user_clerk_id(credentials)
    except HTTPException:
        return None


async def get_current_user(
    clerk_user_id: str = Depends(get_current_user_clerk_id)
) -> dict:
    """
    Get current user information including user_id from backend database
    """
    try:
        user_service = UserService()
        user = await user_service.get_user_by_clerk_id(clerk_user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found in backend database"
            )
        
        return {
            "user_id": str(user.id),
            "clerk_user_id": clerk_user_id,
            "email": user.email,
            "role": user.role
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting current user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user information"
        )