from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from clerk_backend_api import Clerk
from app.core.config import settings
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
    Validate Clerk JWT token and return the user's Clerk ID
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
            
            logger.debug(f"Authenticated user with Clerk ID: {clerk_user_id}")
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