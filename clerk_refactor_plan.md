# Clerk Role Management Refactor Plan

## Executive Summary

The current implementation violates the intended architecture by creating a split-brain system between Clerk and the backend. This plan addresses the architectural issues by making Clerk the single source of truth for user identity and roles, removing redundant backend logic, and implementing proper JWT-based role management.

## Current Architecture Problems

### 1. Split-Brain System
- **Backend**: [`approved_users.json`](backend/config/approved_users.json) + [`RoleService`](backend/app/services/role_service.py) manage roles statically
- **Frontend**: [`AuthContext`](frontend/src/context/AuthContext.tsx) expects roles from Clerk `publicMetadata`
- **Result**: Inconsistent role data between systems, manual synchronization required

### 2. Redundant Role Logic
- [`RoleService`](backend/app/services/role_service.py:12) duplicates Clerk's role management capabilities
- Static JSON file requires manual updates and creates deployment dependencies
- Backend role assignment logic in [`deps.py`](backend/app/api/v1/deps.py:81-83) bypasses Clerk

### 3. Weak JWT Verification
- [`deps.py`](backend/app/api/v1/deps.py:37) uses `verify_signature: False` for development
- No proper JWT verification with Clerk's public keys
- Security vulnerability in production environments

## Code to be Removed

### Backend Files
1. **[`backend/config/approved_users.json`](backend/config/approved_users.json)** - Static role configuration
2. **[`backend/app/services/role_service.py`](backend/app/services/role_service.py)** - Entire service (374 lines)
3. **[`backend/config/backups/`](backend/config/backups/)** - Backup directory for approved users

### Backend Code Sections
1. **[`backend/app/api/v1/deps.py`](backend/app/api/v1/deps.py:81-83)**:
   ```python
   # Remove role assignment logic
   role_service = RoleService()
   assigned_role = role_service.get_role_for_email(primary_email)
   final_role = assigned_role if assigned_role else "client"
   ```

2. **[`backend/app/api/v1/webhooks/clerk.py`](backend/app/api/v1/webhooks/clerk.py:133-134)**:
   ```python
   # Remove static role lookup
   role_service = RoleService()
   assigned_role = role_service.get_role_for_email(primary_email)
   ```

3. **[`backend/app/services/user_service.py`](backend/app/services/user_service.py:36-39)**:
   ```python
   # Remove fallback to RoleService
   from app.services.role_service import RoleService
   role_service = RoleService()
   assigned_role = role_service.get_role_for_email(email)
   ```

4. **[`backend/app/api/v1/endpoints/waitlist.py`](backend/app/api/v1/endpoints/waitlist.py)** - Entire waitlist management system (423 lines) - **PRIORITY REMOVAL**

### Import Statements to Remove
- `from app.services.role_service import RoleService` (5 files)
- All waitlist-related schema imports

## New Architecture Design

### 1. Clerk as Single Source of Truth

#### Standardized Role Storage in Clerk
🟣 **User Role and Organization Clarification**

✅ **Three Primary User Roles:**
- `member`: individuals receiving coaching, with or without org affiliation
- `coach`: business users delivering coaching services, potentially part of a firm/org
- `admin`: Arete internal staff, always linked to Arete's organization (`org_2znowNXOu9Flxs42iQFFl2joDRx`)

```json
// Clerk publicMetadata standardized structure
{
  "primary_role": "member" | "coach" | "admin",
  "default_org_id": "org_123",
  "organization_roles": {
    "org_2znowNXOu9Flxs42iQFFl2joDRx": {
      "role": "admin",
      "permissions": ["manage_members", "view_analytics"]
    },
    "org_456": {
      "role": "coach",
      "permissions": ["view_clients"]
    }
  }
}
```

#### JWT Claims Structure
```json
{
  "sub": "user_123",
  "email": "user@example.com",
  "public_metadata": {
    "primary_role": "coach",
    "default_org_id": "org_456",
    "organization_roles": {
      "org_456": {
        "role": "admin",
        "permissions": ["manage_members", "view_analytics"]
      }
    }
  }
}
```

#### Organization Context Rules
✅ **Endpoints with No Org Requirement (Members):**
- `/api/v1/entries` → Members access regardless of org affiliation, use `primary_role: member`
- `/api/v1/session` → Personal coaching sessions, org context ignored if missing

✅ **Endpoints with Required Org Context (Coaches and Admins):**
- `/api/v1/coach/clients` → Coaches must have valid `organization_roles`, reject if missing
- `/api/v1/org/{org_id}/reporting` → Coaches accessing org-wide reporting must pass org validation
- `/api/v1/admin/analytics` → Admins must belong to Arete org (`org_2znowNXOu9Flxs42iQFFl2joDRx`)

✅ **Validation Rule by Role:**
- `member`: Access allowed without org context, fallback to `primary_role`
- `coach` and `admin`: Reject requests without valid `organization_roles` tied to valid `org_id`

### 2. Session Validation Implementation

#### New JWT Verification Service
```python
# backend/app/services/clerk_jwt_service.py
from clerk_backend_api import Clerk
import jwt
from jwt import PyJWKClient
import logging

class ClerkJWTService:
    def __init__(self):
        self.clerk = Clerk(bearer_auth=settings.clerk_secret_key)
        self.jwks_client = PyJWKClient(
            f"https://api.clerk.com/v1/jwks"
        )
    
    async def verify_and_decode_jwt(self, token: str) -> dict:
        """Verify JWT signature and decode claims"""
        try:
            # Get signing key from Clerk's JWKS endpoint
            signing_key = self.jwks_client.get_signing_key_from_jwt(token)
            
            # Verify and decode token
            decoded_token = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                audience=settings.clerk_frontend_api,
                issuer=f"https://clerk.{settings.clerk_domain}"
            )
            
            return decoded_token
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid JWT token: {e}")
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication token"
            )
    
    def extract_user_roles(self, jwt_payload: dict) -> dict:
        """Extract role information from JWT claims"""
        public_metadata = jwt_payload.get("public_metadata", {})
        
        return {
            "primary_role": public_metadata.get("role", "member"),
            "permissions": public_metadata.get("permissions", []),
            "organization_roles": public_metadata.get("organizationRoles", {})
        }
```

#### Updated Authentication Dependency
```python
# backend/app/api/v1/deps.py
from app.services.clerk_jwt_service import ClerkJWTService

async def get_current_user_clerk_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """Validate Clerk JWT token and return user's Clerk ID"""
    try:
        jwt_service = ClerkJWTService()
        
        # Verify JWT signature and decode
        decoded_token = await jwt_service.verify_and_decode_jwt(
            credentials.credentials
        )
        
        clerk_user_id = decoded_token.get("sub")
        if not clerk_user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid token - no user ID"
            )
        
        # Extract and store role information
        role_data = jwt_service.extract_user_roles(decoded_token)
        
        # Ensure user exists in backend (create if needed)
        await ensure_user_exists(clerk_user_id, decoded_token, role_data)
        
        return clerk_user_id
        
    except Exception as e:
        logger.error(f"JWT validation error: {e}")
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials"
        )
```

### 3. Role Access Implementation

#### Backend Role Access
```python
# backend/app/services/user_role_service.py
class UserRoleService:
    def __init__(self):
        self.jwt_service = ClerkJWTService()
    
    async def get_user_roles_from_token(self, token: str) -> dict:
        """Get user roles directly from JWT token"""
        decoded_token = await self.jwt_service.verify_and_decode_jwt(token)
        return self.jwt_service.extract_user_roles(decoded_token)
    
    def check_permission(self, role_data: dict, permission: str, org_id: str = None) -> bool:
        """Check if user has specific permission"""
        # Check organization-specific permissions first
        if org_id and org_id in role_data.get("organization_roles", {}):
            org_permissions = role_data["organization_roles"][org_id].get("permissions", [])
            if permission in org_permissions:
                return True
        
        # Check global permissions
        return permission in role_data.get("permissions", [])
    
    def has_role(self, role_data: dict, required_role: str, org_id: str = None) -> bool:
        """Check if user has specific role"""
        if org_id and org_id in role_data.get("organization_roles", {}):
            return role_data["organization_roles"][org_id].get("role") == required_role
        
        return role_data.get("primary_role") == required_role
```

#### Frontend Role Access (Already Implemented)
The frontend [`AuthContext`](frontend/src/context/AuthContext.tsx:78) already correctly reads from Clerk's `publicMetadata`:

```typescript
primaryRole: (clerkUser.publicMetadata?.role as 'admin' | 'coach' | 'member') || 'member'
```

### 4. Webhook-based Synchronization

#### Enhanced Clerk Webhook Handler
```python
# backend/app/api/v1/webhooks/clerk.py
@router.post("/clerk")
async def handle_clerk_webhook(request: Request):
    """Handle Clerk user lifecycle webhooks"""
    # ... existing verification code ...
    
    if event_type == "user.created":
        # Extract role from Clerk publicMetadata
        public_metadata = data.get("public_metadata", {})
        primary_role = public_metadata.get("role", "member")
        permissions = public_metadata.get("permissions", [])
        
        # Create user with Clerk-provided role data
        created_user = await user_service.create_user_from_clerk(
            clerk_user_id=clerk_user_id,
            email=primary_email,
            primary_role=primary_role,
            roles=[primary_role],
            permissions=permissions
        )
    
    elif event_type == "user.updated":
        # Sync role changes from Clerk
        public_metadata = data.get("public_metadata", {})
        if "role" in public_metadata:
            await user_service.update_user_role_from_clerk(
                clerk_user_id=data.get("id"),
                role_data=public_metadata
            )
```

#### Database Synchronization (Optional)
If performance requires local role caching:

```python
# backend/app/services/role_sync_service.py
class RoleSyncService:
    """Synchronize role data from Clerk to local database for performance"""
    
    async def sync_user_roles(self, clerk_user_id: str, role_data: dict):
        """Sync role data from Clerk webhook to local database"""
        user = await self.user_repository.get_user_by_clerk_id(clerk_user_id)
        if user:
            await self.user_repository.update_user(str(user.id), {
                "primary_role": role_data.get("role"),
                "permissions": role_data.get("permissions", []),
                "organization_roles": role_data.get("organizationRoles", {}),
                "updated_at": datetime.utcnow()
            })
```

## Implementation Steps

### Phase 1: Waitlist System Elimination + Role Standardization (PRIORITY)
🎯 **Complete Waitlist System Removal + Three-Role Architecture**

Effective immediately, we are eliminating all custom waitlist backend and frontend logic AND standardizing on the three-role system with Clerk-native access controls.

#### Step 1.1: Data Migration to Standardized Clerk Roles
```python
# Migration script to move approved_users.json to standardized Clerk publicMetadata
async def migrate_approved_users_to_clerk():
    """Migrate approved users to standardized three-role system"""
    
    # Read existing approved_users.json
    with open("backend/config/approved_users.json") as f:
        approved_users = json.load(f)
    
    # Update each user in Clerk with standardized role structure
    for user_data in approved_users:
        try:
            # Find user by email in Clerk
            users = clerk.users.list(email_address=[user_data["email"]])
            
            if users.data:
                user = users.data[0]
                
                # Map legacy roles to new system
                legacy_role = user_data["role"]
                primary_role = "member" if legacy_role == "client" else legacy_role
                
                # Build standardized publicMetadata
                public_metadata = {
                    "primary_role": primary_role,
                    "migrated_from": "approved_users.json",
                    "migrated_at": datetime.utcnow().isoformat()
                }
                
                # Add organization_roles for coaches (will be manually assigned later)
                if primary_role in ["coach", "admin"]:
                    public_metadata["organization_roles"] = {}
                    if primary_role == "admin":
                        # Auto-assign admins to Arete org
                        public_metadata["default_org_id"] = "org_2znowNXOu9Flxs42iQFFl2joDRx"
                        public_metadata["organization_roles"]["org_2znowNXOu9Flxs42iQFFl2joDRx"] = {
                            "role": "admin",
                            "permissions": ["manage_members", "view_analytics"]
                        }
                
                clerk.users.update(user_id=user.id, public_metadata=public_metadata)
                logger.info(f"Migrated user {user_data['email']} to {primary_role}")
                
        except Exception as e:
            logger.error(f"Failed to migrate user {user_data['email']}: {e}")
```

#### Step 1.2: Remove Backend Waitlist Code
1. **Delete [`backend/app/api/v1/endpoints/waitlist.py`](backend/app/api/v1/endpoints/waitlist.py)** - Entire 423-line file
2. **Delete [`backend/app/schemas/waitlist.py`](backend/app/schemas/waitlist.py)** - All waitlist schemas
3. **Remove waitlist router** from [`backend/app/main.py`](backend/app/main.py:70)
4. **Delete [`backend/config/approved_users.json`](backend/config/approved_users.json)** and backup directory
5. **Remove [`backend/app/services/role_service.py`](backend/app/services/role_service.py)** entirely (374 lines)

#### Step 1.3: Remove Frontend Waitlist Code
1. **Delete [`frontend/src/app/waitlist/`](frontend/src/app/waitlist/)** directory entirely
2. **Remove waitlist links** from [`frontend/src/app/page.tsx`](frontend/src/app/page.tsx:125,159,357)
3. **Update [`frontend/src/middleware.ts`](frontend/src/middleware.ts:26)** to remove waitlist route
4. **Remove waitlist references** from navigation components

#### Step 1.4: Remove Legacy Approval Gating + Implement Role-Based Access
🎯 **Directive: Remove Legacy `approved` Gating Logic**

We are standardizing product access control **entirely through Clerk's native waitlist functionality**. Remove all `publicMetadata.approved` logic.

```typescript
// Updated AuthContext with standardized three-role system
interface User {
  id: string;
  firstName: string;
  lastName: string;
  email: string;
  primaryRole: 'admin' | 'coach' | 'member';
  defaultOrgId?: string;
  organizationRoles: {
    [orgId: string]: {
      role: string;
      permissions: string[];
    }
  };
  clerkId: string;
}

const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const { user: clerkUser, isLoaded } = useUser();
  
  const user = useMemo((): User | null => {
    if (!clerkUser || !isLoaded) return null;

    const metadata = clerkUser.publicMetadata || {};
    
    return {
      id: clerkUser.id,
      firstName: clerkUser.firstName || '',
      lastName: clerkUser.lastName || '',
      email: clerkUser.emailAddresses[0]?.emailAddress || '',
      primaryRole: metadata.primary_role as 'admin' | 'coach' | 'member' || 'member',
      defaultOrgId: metadata.default_org_id as string,
      organizationRoles: metadata.organization_roles as any || {},
      clerkId: clerkUser.id
    };
  }, [clerkUser, isLoaded]);

  // Role-based access helpers
  const hasOrgAccess = (orgId: string): boolean => {
    return user?.organizationRoles[orgId] !== undefined;
  };

  const requiresOrgContext = (): boolean => {
    return user?.primaryRole === 'coach' || user?.primaryRole === 'admin';
  };

  return (
    <AuthContext.Provider value={{ user, hasOrgAccess, requiresOrgContext }}>
      {children}
    </AuthContext.Provider>
  );
};
```

### Phase 2: Backend Role Validation Enhancement
1. **Create organization validation decorators**:
```python
# backend/app/core/role_decorators.py
def org_required(org_id_param: str = "org_id"):
    """Require valid organization membership for coaches/admins"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract org_id from path params
            org_id = kwargs.get(org_id_param)
            user_roles = get_user_roles_from_jwt(request.headers["authorization"])
            
            # Members don't need org validation
            if user_roles["primary_role"] == "member":
                return await func(*args, **kwargs)
            
            # Coaches/admins must have org membership
            if org_id not in user_roles.get("organization_roles", {}):
                raise HTTPException(403, "Organization access required")
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def org_optional():
    """Allow access with or without org context (members only)"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            user_roles = get_user_roles_from_jwt(request.headers["authorization"])
            
            # Only members can access without org context
            if user_roles["primary_role"] != "member":
                org_roles = user_roles.get("organization_roles", {})
                if not org_roles:
                    raise HTTPException(403, "Organization membership required")
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator
```

2. **Update endpoint validation**:
```python
# Example endpoint implementations
@router.get("/entries")  # No org required for members
@org_optional()
async def get_entries(current_user: str = Depends(get_current_user_clerk_id)):
    # Members can access personal entries regardless of org
    pass

@router.get("/coach/clients")  # Org required for coaches
@org_required()
async def get_coach_clients(current_user: str = Depends(get_current_user_clerk_id)):
    # Coaches must belong to valid org to access clients
    pass

@router.get("/admin/analytics")  # Arete org required for admins
@org_required()
async def get_admin_analytics(current_user: str = Depends(get_current_user_clerk_id)):
    # Admins must belong to Arete org (org_2znowNXOu9Flxs42iQFFl2joDRx)
    pass
```

### Phase 3: JWT Verification Enhancement
1. **Create [`ClerkJWTService`](backend/app/services/clerk_jwt_service.py)** with proper signature verification
2. **Update [`deps.py`](backend/app/api/v1/deps.py)** to extract standardized role structure
3. **Remove all legacy `approved` flag logic** from JWT validation

### Phase 4: Clean Up Legacy Code
1. **Remove all `approved` flag references**:
   - Delete approval checks in API dependencies
   - Remove approval UI states and components
   - Clean up approval-related tests
   - Remove redundant onboarding blockers

2. **Update role assignment flows** to use standardized structure
3. **Document new role structure** in [`DEVELOPMENT.md`](DEVELOPMENT.md)

### Phase 5: Testing and Validation
1. **Test role-based access control** across all three roles
2. **Verify organization context validation** for coaches/admins
3. **Test member access** without org requirements
4. **Validate Arete admin access** to admin-only endpoints
5. **Test new user signup flow** through Clerk waitlist only

## Preventing Future Architectural Drift

### 1. Documentation Updates
- **Update [`DEVELOPMENT.md`](DEVELOPMENT.md)** with Clerk-first architecture principles
- **Create role management guide** emphasizing Clerk as single source of truth
- **Document JWT verification patterns** for new endpoints

### 2. Code Standards
```python
# Add to backend linting rules
# .pylintrc or pyproject.toml
[tool.pylint.messages_control]
disable = [
    "static-role-assignment",  # Custom rule to prevent static role logic
]

# Custom linting rule example
def check_no_static_roles(node):
    """Prevent static role assignment outside of Clerk"""
    if "approved_users" in str(node) or "RoleService" in str(node):
        raise LintError("Use Clerk publicMetadata for role management")
```

### 3. Architecture Decision Records (ADRs)
Create [`docs/adr/001-clerk-single-source-of-truth.md`](docs/adr/001-clerk-single-source-of-truth.md):

```markdown
# ADR-001: Clerk as Single Source of Truth for User Roles

## Status: Accepted

## Context
Previous implementation created split-brain system between Clerk and backend role management.

## Decision
Clerk publicMetadata is the single source of truth for all user roles and permissions.

## Consequences
- All role logic must use JWT claims from Clerk
- No static role files or backend role services allowed
- Role changes must be made through Clerk API or dashboard
```

### 4. Development Guardrails
```python
# backend/app/core/decorators.py
def clerk_roles_only(func):
    """Decorator to ensure role data comes from Clerk JWT"""
    def wrapper(*args, **kwargs):
        # Verify role data source is JWT token
        if hasattr(request, 'role_source') and request.role_source != 'clerk_jwt':
            raise ValueError("Role data must come from Clerk JWT")
        return func(*args, **kwargs)
    return wrapper

# Usage in endpoints
@clerk_roles_only
async def protected_endpoint(current_user: str = Depends(get_current_user_clerk_id)):
    # Endpoint implementation
```

### 5. Testing Strategy
```python
# tests/test_role_architecture.py
def test_no_static_role_files():
    """Ensure no static role files exist"""
    assert not Path("backend/config/approved_users.json").exists()
    assert not Path("backend/app/services/role_service.py").exists()

def test_jwt_verification_enabled():
    """Ensure JWT verification is properly configured"""
    # Test that JWT verification uses proper signature validation
    # Test that role data comes from JWT claims
```

## Migration Strategy

### 1. Data Migration
```python
# migration_script.py
async def migrate_approved_users_to_clerk():
    """One-time migration of approved users to Clerk publicMetadata"""
    
    # Read existing approved_users.json
    with open("backend/config/approved_users.json") as f:
        approved_users = json.load(f)
    
    # Update each user in Clerk
    for user_data in approved_users:
        try:
            # Find user by email in Clerk
            users = clerk.users.list(email_address=[user_data["email"]])
            
            if users.data:
                user = users.data[0]
                
                # Update publicMetadata with role
                clerk.users.update(
                    user_id=user.id,
                    public_metadata={
                        "role": user_data["role"],
                        "permissions": get_permissions_for_role(user_data["role"]),
                        "migrated_from": "approved_users.json",
                        "migrated_at": datetime.utcnow().isoformat()
                    }
                )
                
                logger.info(f"Migrated user {user_data['email']} to Clerk")
                
        except Exception as e:
            logger.error(f"Failed to migrate user {user_data['email']}: {e}")
```

### 2. Rollback Plan
- **Keep backup** of [`approved_users.json`](backend/config/approved_users.json) during migration
- **Feature flag** to switch between old and new access control systems
- **Clerk publicMetadata backup** before removing legacy systems

### 3. Post-Migration Operational Model
✅ **Clerk Dashboard is the single operational touchpoint**:
- Manage invites and approvals directly in Clerk Dashboard
- Set `publicMetadata.approved: true` for user access
- Optional `publicMetadata.beta_invite: true` for staged rollouts
- No separate waitlist database, files, or backend flows

✅ **Zero Backend Maintenance**:
- No custom waitlist logic to maintain
- No static files to update
- All access control through Clerk native capabilities

## Success Metrics

### 1. Architecture Compliance
- ✅ Zero static role files in codebase
- ✅ All role data sourced from Clerk JWT
- ✅ Proper JWT signature verification

### 2. Security Improvements
- ✅ JWT tokens properly verified with Clerk's public keys
- ✅ No hardcoded role assignments
- ✅ Role changes require Clerk API access

### 3. Maintainability
- ✅ Single source of truth for roles
- ✅ Reduced code complexity (374 lines removed)
- ✅ Eliminated manual role file management

## Conclusion

This refactor eliminates the split-brain architecture by making Clerk the authoritative source for user roles AND access control. The implementation prioritizes **complete elimination of custom waitlist logic** in favor of Clerk-native capabilities with simple `publicMetadata.approved` gating.

**Key Simplifications:**
- **800+ lines of waitlist code removed** (waitlist.py + role_service.py + frontend pages)
- **Zero backend maintenance** for access control - all managed through Clerk Dashboard
- **Single gating mechanism**: `publicMetadata.approved: true/false`
- **Operational simplicity**: Clerk Dashboard is the only touchpoint for user access management

The migration removes 800+ lines of redundant code while improving security through proper JWT verification and eliminating all static role/access management. This creates a dramatically simpler, more maintainable, and architecturally sound system aligned with Clerk-native capabilities.

🟣 **The goal is simplicity, speed, and alignment with Clerk-native capabilities.** No backend logic remains for waitlisting, and there is **zero backend maintenance** related to access control.