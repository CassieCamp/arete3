/**
 * Session Refresh Utilities
 * 
 * Handles client-side session refresh when role changes are detected
 * to ensure JWT claims are updated with latest Clerk publicMetadata
 */

import { useAuth } from '@clerk/nextjs';

export interface SessionRefreshOptions {
  forceReload?: boolean;
  redirectTo?: string;
}

/**
 * Hook for session refresh functionality
 */
export function useSessionRefresh() {
  const { signOut, getToken } = useAuth();

  /**
   * Refresh the current session to get updated JWT claims
   */
  const refreshSession = async (options: SessionRefreshOptions = {}) => {
    try {
      console.log('🔄 Refreshing session to get updated role claims...');
      
      // Force token refresh by getting a new token
      const newToken = await getToken({ template: 'default' });
      
      if (newToken) {
        console.log('✅ Session token refreshed successfully');
        
        // If forceReload is true, reload the page to ensure all components get the new token
        if (options.forceReload) {
          console.log('🔄 Reloading page to apply session changes...');
          if (options.redirectTo) {
            window.location.href = options.redirectTo;
          } else {
            window.location.reload();
          }
        }
        
        return true;
      } else {
        console.warn('⚠️ Failed to refresh session token');
        return false;
      }
    } catch (error) {
      console.error('❌ Error refreshing session:', error);
      return false;
    }
  };

  /**
   * Force sign out and redirect to sign in to get fresh session
   */
  const forceSessionReset = async (redirectTo?: string) => {
    try {
      console.log('🔄 Forcing session reset via sign out...');
      
      await signOut({
        redirectUrl: redirectTo || '/sign-in'
      });
      
      return true;
    } catch (error) {
      console.error('❌ Error forcing session reset:', error);
      return false;
    }
  };

  /**
   * Check if current JWT claims match expected role
   */
  const validateRoleClaims = async (expectedRole: string): Promise<boolean> => {
    try {
      const token = await getToken({ template: 'default' });
      
      if (!token) {
        console.warn('⚠️ No token available for role validation');
        return false;
      }

      // Decode JWT to check claims (basic decode, not verification)
      const payload = JSON.parse(atob(token.split('.')[1]));
      const currentRole = payload.publicMetadata?.primary_role;
      
      console.log(`🔍 Role validation: expected=${expectedRole}, current=${currentRole}`);
      
      return currentRole === expectedRole;
    } catch (error) {
      console.error('❌ Error validating role claims:', error);
      return false;
    }
  };

  return {
    refreshSession,
    forceSessionReset,
    validateRoleClaims
  };
}

/**
 * Utility function to refresh session after role changes
 * Can be called from anywhere in the app
 */
export const refreshUserSession = async (options: SessionRefreshOptions = {}) => {
  try {
    // This is a standalone function that doesn't use hooks
    // It triggers a page reload to force session refresh
    console.log('🔄 Triggering session refresh...');
    
    if (options.redirectTo) {
      window.location.href = options.redirectTo;
    } else if (options.forceReload) {
      window.location.reload();
    } else {
      // Trigger a soft refresh by dispatching a custom event
      window.dispatchEvent(new CustomEvent('session-refresh-required'));
    }
    
    return true;
  } catch (error) {
    console.error('❌ Error triggering session refresh:', error);
    return false;
  }
};

/**
 * Session refresh event listener setup
 * Add this to your main layout or app component
 */
export const setupSessionRefreshListener = () => {
  const handleSessionRefresh = () => {
    console.log('🔄 Session refresh event received, reloading page...');
    window.location.reload();
  };

  window.addEventListener('session-refresh-required', handleSessionRefresh);
  
  // Return cleanup function
  return () => {
    window.removeEventListener('session-refresh-required', handleSessionRefresh);
  };
};