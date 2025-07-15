import { useAuth as useClerkAuth, useUser, useOrganization } from '@clerk/nextjs';
import { useCallback } from 'react';

/**
 * Custom hook for making authenticated API calls with proper headers
 */
export function useApiClient() {
  const { getToken } = useClerkAuth();
  const { user } = useUser();
  const { organization } = useOrganization();

  const makeApiCall = useCallback(async (url: string, options: RequestInit = {}) => {
    // Get authentication token
    const token = await getToken();
    if (!token) {
      throw new Error('No authentication token available');
    }

    // Prepare headers
    const headers: Record<string, string> = {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
      ...((options.headers as Record<string, string>) || {})
    };

    // Add organization ID header if user is in an organization context
    if (organization?.id) {
      headers['X-Org-Id'] = organization.id;
    }

    // Remove Content-Type for FormData requests
    if (options.body instanceof FormData) {
      delete headers['Content-Type'];
    }

    const fullUrl = url.startsWith('http') ? url : url;

    return fetch(fullUrl, {
      ...options,
      headers
    });
  }, [getToken, organization?.id]);

  const getAuthToken = useCallback(async (): Promise<string | null> => {
    try {
      return await getToken();
    } catch (error) {
      console.error('Failed to get auth token:', error);
      return null;
    }
  }, [getToken]);

  return {
    makeApiCall,
    getAuthToken,
    user,
    organization
  };
}

/**
 * Legacy compatibility function for components that still use the old pattern
 */
export function useAuth() {
  const { getToken } = useClerkAuth();
  const { user } = useUser();
  const { organization } = useOrganization();

  const getAuthToken = async (): Promise<string | null> => {
    try {
      return await getToken();
    } catch (error) {
      console.error('Failed to get auth token:', error);
      return null;
    }
  };

  return {
    getAuthToken,
    user,
    organization,
    // Legacy properties for backward compatibility
    isAuthenticated: !!user,
    roleLoaded: true
  };
}