import { useCallback } from 'react';
import { useAuth } from '@/context/AuthContext';
import { useToast } from './use-toast';

export interface ApiClientOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  headers?: HeadersInit;
  body?: any;
  baseUrl?: string;
}

export interface ApiResponse<T = any> {
  data: T;
  status: number;
  headers: Headers;
}

/**
 * Custom hook that provides a centralized API client with automatic JWT refresh detection
 */
export function useApiClient() {
  const { getAuthToken } = useAuth();
  const { toast } = useToast();

  const makeApiCall = useCallback(async <T = any>(
    endpoint: string,
    options: ApiClientOptions = {}
  ): Promise<ApiResponse<T>> => {
    const {
      method = 'GET',
      headers: customHeaders = {},
      body,
      baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'
    } = options;

    // Get authentication token
    const token = await getAuthToken();
    if (!token) {
      throw new Error('Authentication token is required');
    }

    // Prepare headers
    const headers: Record<string, string> = {
      'Authorization': `Bearer ${token}`,
      ...(customHeaders as Record<string, string>)
    };

    // Add Content-Type for JSON requests if body is provided and not FormData
    if (body && !(body instanceof FormData)) {
      headers['Content-Type'] = 'application/json';
    }

    // Construct full URL
    const url = endpoint.startsWith('http') ? endpoint : `${baseUrl}${endpoint}`;

    // Prepare request body
    let requestBody: any = body;
    if (body && !(body instanceof FormData) && typeof body === 'object') {
      requestBody = JSON.stringify(body);
    }

    // Make the API call
    const response = await fetch(url, {
      method,
      headers,
      body: requestBody,
    });

    // Check for session refresh header
    const refreshHeader = response.headers.get('X-Session-Refresh-Required');
    if (refreshHeader === 'true') {
      // Display toast notification to user
      toast({
        title: 'Session Refreshing',
        description: 'Your session is being refreshed for security. The page will reload momentarily.',
        variant: 'default'
      });

      // Small delay to ensure toast is visible before reload
      setTimeout(() => {
        window.location.reload();
      }, 1500);

      // Return early to prevent further processing
      throw new Error('Session refresh required - page will reload');
    }

    // Parse response
    let data: T;
    const contentType = response.headers.get('content-type');
    
    if (contentType && contentType.includes('application/json')) {
      data = await response.json();
    } else {
      data = await response.text() as unknown as T;
    }

    // Handle non-OK responses
    if (!response.ok) {
      const errorMessage = typeof data === 'object' && data && 'detail' in data 
        ? (data as any).detail 
        : `HTTP error! status: ${response.status}`;
      throw new Error(errorMessage);
    }

    return {
      data,
      status: response.status,
      headers: response.headers,
    };
  }, [getAuthToken, toast]);

  // Convenience methods for common HTTP verbs
  const get = useCallback(<T = any>(endpoint: string, options: Omit<ApiClientOptions, 'method'> = {}) => {
    return makeApiCall<T>(endpoint, { ...options, method: 'GET' });
  }, [makeApiCall]);

  const post = useCallback(<T = any>(endpoint: string, body?: any, options: Omit<ApiClientOptions, 'method' | 'body'> = {}) => {
    return makeApiCall<T>(endpoint, { ...options, method: 'POST', body });
  }, [makeApiCall]);

  const put = useCallback(<T = any>(endpoint: string, body?: any, options: Omit<ApiClientOptions, 'method' | 'body'> = {}) => {
    return makeApiCall<T>(endpoint, { ...options, method: 'PUT', body });
  }, [makeApiCall]);

  const del = useCallback(<T = any>(endpoint: string, options: Omit<ApiClientOptions, 'method'> = {}) => {
    return makeApiCall<T>(endpoint, { ...options, method: 'DELETE' });
  }, [makeApiCall]);

  const patch = useCallback(<T = any>(endpoint: string, body?: any, options: Omit<ApiClientOptions, 'method' | 'body'> = {}) => {
    return makeApiCall<T>(endpoint, { ...options, method: 'PATCH', body });
  }, [makeApiCall]);

  return {
    makeApiCall,
    get,
    post,
    put,
    delete: del,
    patch,
  };
}