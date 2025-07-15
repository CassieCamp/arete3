# Navigation Role Sync Fix - July 14, 2025

## Summary
Members were incorrectly shown the "Profile" tab in main navigation. The Profile tab should only be visible to coaches, but was appearing for all member users due to improper role configuration.

## Root Cause Analysis
The navigation system used a shared `MAIN_NAVIGATION` array where navigation items contained multiple roles in a single `roles` array. The Profile navigation item incorrectly included both `'member'` and `'coach'` roles, causing it to be displayed to member users through the filtering logic in `NavigationProvider.tsx`.

**Specific Issue:**
```typescript
// In frontend/src/config/navigation.ts
{
  id: 'profile',
  roles: ['member', 'coach'], // ❌ This caused the leak
  // ...
}
```

## Solution Applied
**Immediate Fix:** Removed `'member'` from the Profile navigation item's roles array, restricting it to coaches only.

**Architectural Improvement:** Refactored the navigation system to use role-specific navigation arrays (`MEMBER_NAVIGATION`, `COACH_NAVIGATION`, `ADMIN_NAVIGATION`) instead of runtime filtering, eliminating the possibility of role leakage.

## Preventative Measures
1. **Separated Navigation by Role:** Created distinct navigation arrays for each role to prevent cross-contamination
2. **Eliminated Runtime Filtering:** NavigationProvider now uses direct role-based imports instead of `.filter()` operations
3. **Added Unit Tests:** Created comprehensive tests at `/frontend/src/config/__tests__/navigation.test.ts` to verify each role sees only their intended navigation items
4. **Documentation:** Added preventative comments explaining the rationale for role separation
5. **Optional Linting:** Considered ESLint rule to flag `.filter()` usage on navigation arrays

## Follow-Up Notes
This incident highlighted the need for compile-time safety in role-based UI components. The new architecture makes role boundaries explicit and prevents similar leakage issues across the application.

**Verification:** UAT confirmed that members now see only "Journey", "Center", and "Coaching" tabs, with Profile correctly hidden.

---
*Logged by Roo Code — initiated by @cassie*