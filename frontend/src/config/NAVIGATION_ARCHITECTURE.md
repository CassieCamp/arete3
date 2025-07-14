# Navigation Architecture Documentation

## Overview

This document explains the role-based navigation architecture implemented to prevent UI element leakage between different user roles.

## Architecture Principles

### 1. Role Separation by Design
- **Each role has its own dedicated navigation array**
- **No shared arrays with runtime filtering**
- **Compile-time safety through direct role mapping**

### 2. Single Source of Truth
- Each role's navigation is defined once in its dedicated array
- No duplication or cross-referencing between role arrays
- Clear ownership and responsibility for each navigation set

### 3. Explicit Role Mapping
- Direct function calls: `getMainNavigationForRole('member')`
- No complex filtering logic in components
- TypeScript ensures only valid roles are used

## File Structure

```
frontend/src/config/
├── navigation.ts              # Main navigation configuration
├── __tests__/
│   └── navigation.test.ts     # Comprehensive role isolation tests
└── NAVIGATION_ARCHITECTURE.md # This documentation
```

## Navigation Arrays

### Member Navigation (`MEMBER_NAVIGATION`)
```typescript
// Users with primary_role: 'member'
- Journey (/member/journey)
- Center (/member/center) 
- Coaching (/member/coaching)
```

### Coach Navigation (`COACH_NAVIGATION`)
```typescript
// Users with primary_role: 'coach'
- Practice (/coach/practice)
- Clients (/coach/clients)
- Profile (/coach/profile)
```

### Admin Navigation (`ADMIN_NAVIGATION`)
```typescript
// Users with primary_role: 'admin'
- Organizations (/organizations)
```

## Usage Patterns

### ✅ Correct Usage
```typescript
// In NavigationProvider.tsx
const roleMainNavigation = getMainNavigationForRole(navigationRole);
const roleMenuNavigation = getMenuNavigationForRole(navigationRole);
```

### ❌ Incorrect Usage (Deprecated)
```typescript
// DON'T DO THIS - causes role leakage
const filteredNavigation = MAIN_NAVIGATION.filter(item => 
  item.roles.includes(userRole)
);
```

## Key Benefits

1. **Prevents Role Leakage**: Impossible for navigation items to appear in wrong roles
2. **Compile-Time Safety**: TypeScript catches invalid role usage
3. **Performance**: Direct array access vs runtime filtering
4. **Maintainability**: Clear separation of concerns
5. **Testability**: Each role can be tested independently

## Testing Strategy

The test suite (`navigation.test.ts`) verifies:
- Each role sees only their intended navigation items
- No navigation item appears in multiple role arrays
- Specific regression prevention (e.g., Profile tab only for coaches)
- Navigation item structure consistency
- Role isolation verification

## Migration Notes

### From Legacy System
The old system used:
- Shared `MAIN_NAVIGATION` array with `roles` properties
- Runtime filtering in `NavigationProvider`
- Complex legacy role mapping

### To New System
The new system uses:
- Role-specific arrays (`MEMBER_NAVIGATION`, `COACH_NAVIGATION`, etc.)
- Direct role mapping functions
- Simplified NavigationProvider logic

## Maintenance Guidelines

### Adding New Navigation Items

1. **Identify the target role(s)**
2. **Add to the appropriate role-specific array(s)**
3. **Update tests to verify the new item appears correctly**
4. **Never add to shared arrays or use runtime filtering**

### Example: Adding a new member-only item
```typescript
// In MEMBER_NAVIGATION array
{
  id: 'new-feature',
  icon: NewFeatureIcon,
  label: 'New Feature',
  description: 'Description of new feature',
  href: '/member/new-feature'
}
```

### Modifying Existing Items

1. **Locate the item in its role-specific array**
2. **Make changes directly in that array**
3. **Update tests if navigation structure changes**
4. **Verify no other roles are affected**

## Troubleshooting

### Navigation Item Not Appearing
1. Check if item is in correct role-specific array
2. Verify user's `primary_role` matches expected role
3. Check NavigationProvider role mapping logic
4. Ensure no TypeScript errors in navigation config

### Navigation Item Appearing in Wrong Role
1. Check if item was accidentally added to multiple role arrays
2. Run tests to verify role isolation
3. Check NavigationProvider role mapping logic

### Performance Issues
1. Verify direct role mapping is being used (not filtering)
2. Check for unnecessary re-renders in NavigationProvider
3. Ensure navigation arrays are not being recreated on each render

## Future Considerations

### Scalability
- Consider role hierarchies if needed (e.g., admin inherits coach permissions)
- Evaluate need for dynamic navigation based on organization context
- Plan for feature flags affecting navigation visibility

### Extensibility
- Design allows for easy addition of new roles
- Permission-based navigation can be layered on top
- Organization-specific navigation can be added as needed

## Related Files

- `frontend/src/components/navigation/NavigationProvider.tsx` - Uses role-specific navigation
- `frontend/src/components/navigation/TopNav.tsx` - Renders navigation items
- `internal-docs/architecture-notes/2025-07-14-navigation-role-sync-fix.md` - Incident log

---

**Remember**: The goal is to make role leakage impossible through architecture, not just unlikely through careful coding.