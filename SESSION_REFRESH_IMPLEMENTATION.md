# Session Refresh Implementation Guide

## Overview

This document outlines the comprehensive session refresh system implemented to resolve JWT claim staleness when Clerk publicMetadata changes. The system ensures that role changes in Clerk are immediately reflected in user sessions across the application.

## Problem Statement

**Original Issue**: When user roles are updated in Clerk's publicMetadata, JWT tokens remain stale and don't reflect the new role information until the user manually signs out and back in.

**Evidence**:
- ✅ Clerk publicMetadata: `"primary_role": "coach"` (CORRECT)
- ❌ JWT Claims: `"primary_role": "member"` (STALE)
- ✅ Frontend functionality works (user can access correct routes)
- ❌ Backend logs show incorrect role from JWT claims

## Solution Architecture

### 1. Backend Session Refresh (Webhook-Based)

**File**: `backend/app/api/v1/webhooks/clerk.py`

**Implementation**:
- Enhanced `user.updated` webhook to detect `publicMetadata.primary_role` changes
- Uses Clerk's `sessions.revoke_session()` API to invalidate all active sessions
- Fallback to ban/unban approach if session revocation fails
- Automatic session refresh when roles change via Clerk dashboard

**Key Features**:
```python
# Get all active sessions
sessions = clerk_client.users.get_user_sessions(user_id=clerk_user_id)

# Revoke each session
for session in sessions:
    clerk_client.sessions.revoke_session(session_id=session.id)
```

### 2. Migration Script Session Refresh

**File**: `backend/migrations/s11_1_migrate_users_to_clerk_metadata.py`

**Implementation**:
- Updated migration script to automatically refresh sessions after role updates
- Uses same session revocation approach as webhook
- Ensures bulk role migrations don't leave stale sessions

**Key Features**:
```python
def invalidate_user_sessions(self, user_id: str, email: str) -> bool:
    """Refresh user sessions by revoking active sessions after role update"""
    sessions = self.clerk_client.users.get_user_sessions(user_id=user_id)
    # Revoke all sessions...
```

### 3. Client-Side Session Refresh Utilities

**File**: `frontend/src/utils/sessionRefresh.ts`

**Implementation**:
- React hooks for session refresh functionality
- Token refresh utilities using Clerk's `getToken()` API
- Session validation helpers
- Event-based session refresh system

**Key Features**:
```typescript
export function useSessionRefresh() {
  const { getToken } = useAuth();
  
  const refreshSession = async (options: SessionRefreshOptions = {}) => {
    const newToken = await getToken({ template: 'default' });
    // Handle refresh...
  };
}
```

### 4. Backend Session Validation Middleware

**File**: `backend/app/middleware/session_validation.py`

**Implementation**:
- Middleware to detect stale JWT claims
- Compares JWT claims against current Clerk publicMetadata
- Adds response headers to indicate session staleness
- Optional strict mode to block stale sessions

**Key Features**:
```python
async def validate_session_freshness(self, clerk_user_id: str, jwt_claims: Dict[str, Any]):
    # Get current Clerk data
    clerk_user = self.clerk_client.users.get(user_id=clerk_user_id)
    current_metadata = clerk_user.public_metadata or {}
    
    # Compare with JWT claims
    role_mismatch = current_primary_role != jwt_primary_role
```

### 5. Enhanced Authentication Dependencies

**File**: `backend/app/api/v1/deps.py`

**Implementation**:
- Integrated session validation into authentication flow
- Non-blocking validation by default
- Logs warnings for stale sessions
- Removed all fallbacks to backend-stored roles

## Implementation Details

### Session Refresh Flow

1. **Role Change Trigger**:
   - Admin updates user role in Clerk dashboard
   - Migration script updates roles in bulk

2. **Webhook Processing**:
   - `user.updated` webhook detects `publicMetadata.primary_role` change
   - System fetches all active sessions for the user
   - All sessions are revoked using Clerk API

3. **User Experience**:
   - User's next request will require fresh authentication
   - New JWT token contains updated role information
   - User automatically redirected to appropriate dashboard

4. **Fallback Mechanisms**:
   - If session revocation fails, fallback to ban/unban approach
   - If webhook fails, manual session refresh utilities available
   - Session validation middleware detects and logs stale sessions

### Response Headers

The system adds helpful headers to API responses:

```
X-Session-Refresh-Recommended: true
X-Session-Stale-Reason: role-mismatch
X-Expected-Role: coach
X-Current-JWT-Role: member
```

### Client-Side Integration

Frontend can detect stale sessions and trigger refresh:

```typescript
// Check for stale session headers
if (response.headers.get('X-Session-Refresh-Recommended')) {
  const { refreshSession } = useSessionRefresh();
  await refreshSession({ forceReload: true });
}
```

## Configuration Options

### Strict Mode

Enable strict session validation to block stale sessions:

```python
validation_result = await validate_user_session(
    request, clerk_user_id, decoded_token, strict_mode=True
)
```

### JWT Expiration Tuning

Consider shorter JWT expiration for role-sensitive operations:

```javascript
// In Clerk dashboard: JWT Template settings
// Reduce token lifetime for faster role propagation
```

## Testing & Verification

### Test Scenarios

1. **Role Change via Clerk Dashboard**:
   - Update user role in Clerk
   - Verify webhook triggers session refresh
   - Confirm user gets new role on next request

2. **Bulk Migration**:
   - Run migration script
   - Verify all affected users get session refresh
   - Confirm no stale sessions remain

3. **Session Validation**:
   - Simulate stale session
   - Verify middleware detects staleness
   - Confirm appropriate headers are added

### Monitoring

Monitor these log messages:

```
✅ Successfully revoked N sessions for user X
⚠️ Stale session detected for user X
🔄 Primary role changed, refreshing sessions
```

## Security Considerations

1. **Session Revocation**: Immediately invalidates compromised sessions
2. **Fallback Protection**: Multiple layers ensure session refresh works
3. **Non-Blocking Validation**: Doesn't break user experience during validation failures
4. **Audit Trail**: Comprehensive logging of all session refresh activities

## Future Enhancements

1. **Real-Time Notifications**: WebSocket notifications for role changes
2. **Selective Refresh**: Only refresh sessions for specific role changes
3. **Session Analytics**: Track session refresh patterns and performance
4. **Client-Side Caching**: Intelligent token caching with staleness detection

## Troubleshooting

### Common Issues

1. **Sessions Not Refreshing**:
   - Check webhook configuration in Clerk dashboard
   - Verify `CLERK_SECRET_KEY` is correct
   - Check network connectivity to Clerk API

2. **Stale Session Warnings**:
   - Normal during role transitions
   - Should resolve after user's next sign-in
   - Enable strict mode if blocking is required

3. **Performance Impact**:
   - Session validation adds minimal overhead
   - Webhook processing is asynchronous
   - Consider caching for high-traffic scenarios

### Debug Commands

```bash
# Check webhook logs
grep "user.updated" backend/logs/app.log

# Verify session refresh
grep "Successfully revoked" backend/logs/app.log

# Monitor stale sessions
grep "Stale session detected" backend/logs/app.log
```

## Conclusion

This comprehensive session refresh system ensures that role changes in Clerk are immediately reflected across the application, eliminating the JWT staleness issue while maintaining a smooth user experience. The multi-layered approach provides robust fallback mechanisms and comprehensive monitoring capabilities.