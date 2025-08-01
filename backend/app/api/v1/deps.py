from fastapi import Depends, HTTPException, status, WebSocket, Query, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from clerk_backend_api import Clerk
from app.core.config import settings
from app.services.user_service import UserService
from app.services.clerk_organization_service import ClerkOrganizationService
from app.services.analysis_service import AnalysisService
from app.repositories.baseline_repository import BaselineRepository
from app.repositories.document_repository import DocumentRepository
from app.middleware.session_validation import validate_user_session
import logging
import jwt
from jwt import PyJWKClient
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError, InvalidSignatureError
import httpx
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer()

# JWKS Cache for JWT verification
class JWKSCache:
    def __init__(self):
        self.jwks_data = None
        self.last_updated = None
        self.cache_duration = timedelta(hours=24)  # Cache for 24 hours
        self.jwks_url = None  # Will be determined from JWT issuer
        
    async def get_jwks(self, issuer: str) -> Dict[str, Any]:
        """Get JWKS data, refreshing cache if needed"""
        # Construct JWKS URL from issuer
        if issuer.endswith('/'):
            issuer = issuer[:-1]
        jwks_url = f"{issuer}/.well-known/jwks.json"
        
        now = datetime.utcnow()
        
        # Check if cache is valid and URL hasn't changed
        if (self.jwks_data is not None and
            self.last_updated is not None and
            self.jwks_url == jwks_url and
            now - self.last_updated < self.cache_duration):
            return self.jwks_data
        
        # Update URL and fetch fresh JWKS data
        self.jwks_url = jwks_url
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.jwks_url, timeout=10.0)
                response.raise_for_status()
                
                self.jwks_data = response.json()
                self.last_updated = now
                logger.info(f"✅ JWKS cache refreshed from {self.jwks_url}")
                return self.jwks_data
                
        except Exception as e:
            logger.error(f"❌ Failed to fetch JWKS from {self.jwks_url}: {e}")
            if self.jwks_data is not None:
                logger.warning("🔄 Using stale JWKS cache due to fetch failure")
                return self.jwks_data
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Unable to verify tokens: JWKS unavailable"
            )
    
    def find_key_by_kid(self, jwks_data: Dict[str, Any], kid: str) -> Optional[Dict[str, Any]]:
        """Find a specific key by its Key ID (kid)"""
        keys = jwks_data.get("keys", [])
        for key in keys:
            if key.get("kid") == kid:
                return key
        return None

# Global JWKS cache instance
jwks_cache = JWKSCache()

async def verify_clerk_jwt(token: str) -> Dict[str, Any]:
    """
    Securely verify Clerk JWT token using JWKS
    """
    try:
        # First decode without verification to get issuer and kid
        unverified_payload = jwt.decode(token, options={"verify_signature": False})
        unverified_header = jwt.get_unverified_header(token)
        
        kid = unverified_header.get("kid")
        issuer = unverified_payload.get("iss")
        
        if not kid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing key ID",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not issuer:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing issuer",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get JWKS data using the issuer
        jwks_data = await jwks_cache.get_jwks(issuer)
        
        # Find the matching key
        key_data = jwks_cache.find_key_by_kid(jwks_data, kid)
        if not key_data:
            # Key not found, refresh cache and try again
            logger.warning(f"🔄 Key ID {kid} not found in cache, refreshing JWKS")
            jwks_cache.last_updated = None  # Force cache refresh
            jwks_data = await jwks_cache.get_jwks(issuer)
            key_data = jwks_cache.find_key_by_kid(jwks_data, kid)
            
            if not key_data:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: key not found",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        
        # Create PyJWK from key data
        from jwt import PyJWK
        key = PyJWK(key_data)
        
        # Verify and decode the token
        decoded_token = jwt.decode(
            token,
            key.key,
            algorithms=["RS256"],  # Clerk uses RS256
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_iat": True,
                "verify_aud": False,  # Clerk doesn't always set audience
                "verify_iss": True,
            },
            issuer=issuer,  # Use the issuer from the token
        )
        
        logger.info(f"✅ JWT signature verified successfully for user: {decoded_token.get('sub')}")
        return decoded_token
        
    except ExpiredSignatureError:
        logger.warning("🔒 JWT token has expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except InvalidSignatureError:
        logger.error("🔒 JWT signature verification failed")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token signature",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except InvalidTokenError as e:
        logger.error(f"🔒 Invalid JWT token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"❌ JWT verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_clerk_id(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    Validate Clerk JWT token using secure JWKS verification, ensure user exists in backend database, and return user info with roles
    """
    try:
        # Securely verify the JWT token with Clerk's JWKS
        token = credentials.credentials
        
        try:
            # Use secure JWT verification with JWKS
            decoded_token = await verify_clerk_jwt(token)
            clerk_user_id = decoded_token.get("sub")
            
            if not clerk_user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication token - no user ID",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Fetch real-time organization roles from Clerk to ensure data is fresh
            clerk_org_service = ClerkOrganizationService()
            try:
                user_orgs = await clerk_org_service.get_user_organizations(clerk_user_id)
                organization_roles = {
                    org["id"]: {"role": org["role"]} for org in user_orgs
                }
                
                # Extract user's first and last name from organization data
                first_name = ""
                last_name = ""
                if user_orgs:
                    public_user_data = user_orgs[0].get("public_user_data", {})
                    first_name = public_user_data.get("first_name", "")
                    last_name = public_user_data.get("last_name", "")

                # Determine primary_role based on the most privileged role found
                is_coach_or_admin = any(
                    org["role"] in ["admin", "coach"] for org in user_orgs
                )
                
                jwt_primary_role = decoded_token.get("publicMetadata", {}).get("primary_role", "member")
                primary_role = "coach" if is_coach_or_admin else jwt_primary_role
                logger.info(f"✅ Successfully fetched real-time roles from Clerk for user {clerk_user_id}.")

            except Exception as e:
                logger.error(f"❌ Failed to fetch organization roles from Clerk for user {clerk_user_id}: {e}")
                # Fallback to JWT roles if Clerk call fails
                public_metadata = decoded_token.get("publicMetadata", {})
                primary_role = public_metadata.get("primary_role", "member")
                organization_roles = public_metadata.get("organization_roles", {})
                logger.warning(f"⚠️ Using potentially stale roles from JWT for user {clerk_user_id}.")

            logger.info(f"🔍 Authenticated user with Clerk ID: {clerk_user_id}")
            logger.info(f"🔍 Effective Primary role: {primary_role}, Organization roles: {organization_roles}")
            
            # Validate session freshness (non-blocking by default)
            try:
                validation_result = await validate_user_session(
                    request, clerk_user_id, decoded_token, strict_mode=False
                )
                
                if validation_result.get("refresh_recommended"):
                    logger.warning(
                        f"⚠️ Stale session detected for {clerk_user_id}: "
                        f"Clerk role='{validation_result.get('clerk_primary_role')}', "
                        f"JWT role='{validation_result.get('jwt_primary_role')}'"
                    )
                
            except Exception as validation_error:
                logger.error(f"❌ Session validation error for {clerk_user_id}: {validation_error}")
                # Continue with authentication even if validation fails
            
            # The user is authenticated by Clerk, no need to check our database.
            return {
                "clerk_user_id": clerk_user_id,
                "primary_role": primary_role,
                "organization_roles": organization_roles,
                "first_name": first_name,
                "last_name": last_name
            }
            
        except HTTPException:
            # Re-raise HTTP exceptions from verify_clerk_jwt
            raise
        
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


def get_analysis_service() -> AnalysisService:
    """
    Get AnalysisService instance with required dependencies
    """
    baseline_repository = BaselineRepository()
    document_repository = DocumentRepository()
    return AnalysisService(baseline_repository, document_repository)


async def get_current_user_websocket(websocket: WebSocket, token: str = Query(...)):
    """Get current user from WebSocket connection with token as query parameter using secure JWT verification"""
    logger.info(f"=== get_current_user_websocket called ===")
    logger.info(f"Token received: {token[:20]}..." if token else "No token")
    
    try:
        user_service = UserService()
        
        # Securely verify the JWT token using JWKS
        decoded_token = await verify_clerk_jwt(token)
        clerk_user_id = decoded_token.get("sub")
        
        if not clerk_user_id:
            logger.error("No clerk_user_id found in token")
            raise HTTPException(status_code=401, detail="Invalid token")
        
        logger.info(f"🔍 Authenticated WebSocket user with Clerk ID: {clerk_user_id}")
        
        # Get user from Clerk
        user = user_service.get_user(clerk_user_id)
        if not user:
            logger.error(f"User not found for clerk_id: {clerk_user_id}")
            raise HTTPException(status_code=401, detail="User not found")

        def get_primary_email(user):
            if not user or not user.email_addresses:
                return None
            for email in user.email_addresses:
                if email.id == user.primary_email_address_id:
                    return email.email_address
            return user.email_addresses[0].email_address
        
        logger.info(f"✅ WebSocket User {clerk_user_id} found via Clerk")
        
        # Extract role information from JWT token
        public_metadata = decoded_token.get("publicMetadata", {})
        primary_role = public_metadata.get("primary_role", "member")
        
        return {
            "clerk_user_id": clerk_user_id,
            "email": get_primary_email(user),
            "primary_role": primary_role  # Always use Clerk JWT claims
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions from verify_clerk_jwt
        raise
    except Exception as e:
        logger.error(f"❌ Error in get_current_user_websocket: {e}")
        raise HTTPException(status_code=401, detail="Could not validate credentials")


# Organization-based Access Control Decorators

async def org_required(
    request: Request,
    user_info: Dict[str, Any] = Depends(get_current_user_clerk_id)
) -> Dict[str, Any]:
    """
    Decorator for endpoints that require organization membership with coach or admin role.
    
    This dependency:
    1. Ensures the user is authenticated
    2. Checks that primary_role is not 'member' (members cannot access org-specific endpoints)
    3. Validates presence of X-Org-Id header
    4. Verifies user has coach or admin role in the specified organization
    
    Returns user info with validated organization context.
    """
    try:
        clerk_user_id = user_info["clerk_user_id"]
        primary_role = user_info["primary_role"]
        organization_roles = user_info["organization_roles"]
        
        logger.info(f"🔒 org_required: Checking access for user {clerk_user_id}")
        logger.info(f"🔒 Primary role: {primary_role}, Organization roles: {organization_roles}")
        
        # Step 1: Check for X-Org-Id header
        org_id = request.headers.get("X-Org-Id")
        if not org_id:
            logger.warning(f"🔒 Access denied: Missing X-Org-Id header for user {clerk_user_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization ID required in X-Org-Id header"
            )
        
        logger.info(f"🔒 Checking organization access for org_id: {org_id}")
        
        # Step 2: Check if the user has a role that allows access to org endpoints
        if primary_role == "member":
            logger.warning(f"🔒 Access denied: User {clerk_user_id} has primary role 'member', which is not sufficient for this endpoint.")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Your role does not permit access to this resource."
            )

        # Step 3: Check organization membership and role
        if org_id not in organization_roles:
            logger.warning(f"🔒 Access denied: User {clerk_user_id} not member of organization {org_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: Not a member of organization {org_id}"
            )
        
        # Step 4: Check role within organization
        org_role_info = organization_roles[org_id]
        org_role = org_role_info.get("role") if isinstance(org_role_info, dict) else org_role_info
        
        if org_role not in ["coach", "admin"]:
            logger.warning(f"🔒 Access denied: User {clerk_user_id} has role '{org_role}' in org {org_id}, requires coach or admin")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: Requires coach or admin role in organization {org_id}"
            )
        
        logger.info(f"✅ org_required: Access granted for user {clerk_user_id} with role '{org_role}' in org {org_id}")
        
        # Return user info with organization context
        return {
            **user_info,
            "org_id": org_id,
            "org_role": org_role
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error in org_required: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to validate organization access"
        )


async def org_optional(
    request: Request,
    user_info: Dict[str, Any] = Depends(get_current_user_clerk_id)
) -> Dict[str, Any]:
    """
    Decorator for endpoints that can operate with or without organization context.
    
    This dependency:
    1. Ensures the user is authenticated (any role including 'member')
    2. Optionally checks for X-Org-Id header
    3. If org_id provided, validates user has access to that organization
    4. Returns user info with optional organization context
    
    This is suitable for endpoints that members can access, but may have enhanced
    functionality when accessed within an organization context.
    """
    try:
        clerk_user_id = user_info["clerk_user_id"]
        primary_role = user_info["primary_role"]
        organization_roles = user_info["organization_roles"]
        
        logger.info(f"🔓 org_optional: Processing request for user {clerk_user_id}")
        
        # Check for optional X-Org-Id header
        org_id = request.headers.get("X-Org-Id")
        
        if not org_id:
            # No organization context - return basic user info
            logger.info(f"🔓 org_optional: No organization context for user {clerk_user_id}")
            return {
                **user_info,
                "org_id": None,
                "org_role": None
            }
        
        logger.info(f"🔓 org_optional: Checking organization context for org_id: {org_id}")
        
        # Organization context provided - validate access
        if org_id not in organization_roles:
            logger.warning(f"🔓 org_optional: User {clerk_user_id} not member of organization {org_id}, proceeding without org context")
            return {
                **user_info,
                "org_id": None,
                "org_role": None
            }
        
        # User has access to organization - include org context
        org_role_info = organization_roles[org_id]
        org_role = org_role_info.get("role") if isinstance(org_role_info, dict) else org_role_info
        
        logger.info(f"✅ org_optional: Organization context validated for user {clerk_user_id} with role '{org_role}' in org {org_id}")
        
        return {
            **user_info,
            "org_id": org_id,
            "org_role": org_role
        }
        
    except Exception as e:
        logger.error(f"❌ Error in org_optional: {e}")
        # For org_optional, we don't want to fail the request on org validation errors
        # Return basic user info without organization context
        logger.info(f"🔓 org_optional: Falling back to basic user info due to error")
        return {
            **user_info,
            "org_id": None,
            "org_role": None
        }