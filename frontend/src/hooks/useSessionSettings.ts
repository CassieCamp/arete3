import { useState, useEffect, useCallback } from 'react';
import { useApiClient } from '@/utils/api';

interface SessionSettings {
  session_auto_send_context: boolean;
}

interface SessionSettingsUpdateRequest {
  session_auto_send_context: boolean;
}

interface SessionSettingsUpdateResponse {
  message: string;
  session_auto_send_context: boolean;
}

/**
 * Custom hook to manage session settings for members
 */
export function useSessionSettings() {
  const { makeApiCall } = useApiClient();
  const [settings, setSettings] = useState<SessionSettings>({ session_auto_send_context: false });
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isUpdating, setIsUpdating] = useState(false);

  useEffect(() => {
    let isMounted = true;

    const fetchSettings = async () => {
      try {
        setIsLoading(true);
        setError(null);

        const response = await makeApiCall('/api/v1/member/session-settings/');
        
        if (!response.ok) {
          throw new Error(`Failed to fetch session settings: ${response.status}`);
        }
        
        const data: SessionSettings = await response.json();
        
        if (isMounted) {
          setSettings(data);
        }
      } catch (err) {
        if (isMounted) {
          const errorMessage = err instanceof Error ? err.message : 'Failed to fetch session settings';
          setError(errorMessage);
          console.error('Error fetching session settings:', err);
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    fetchSettings();

    return () => {
      isMounted = false;
    };
  }, [makeApiCall]);

  const updateSettings = useCallback(async (newSettings: Partial<SessionSettings>) => {
    try {
      setIsUpdating(true);
      setError(null);

      // Optimistic update
      const previousSettings = settings;
      setSettings(prev => ({ ...prev, ...newSettings }));

      const response = await makeApiCall('/api/v1/member/session-settings/', {
        method: 'PUT',
        body: JSON.stringify(newSettings)
      });
      
      if (!response.ok) {
        // Revert optimistic update on error
        setSettings(previousSettings);
        throw new Error(`Failed to update session settings: ${response.status}`);
      }
      
      const data: SessionSettingsUpdateResponse = await response.json();
      
      // Update with server response to ensure consistency
      setSettings({ session_auto_send_context: data.session_auto_send_context });
      
      return data;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to update session settings';
      setError(errorMessage);
      console.error('Error updating session settings:', err);
      throw err;
    } finally {
      setIsUpdating(false);
    }
  }, [makeApiCall, settings]);

  const toggleAutoSendContext = useCallback(async () => {
    return updateSettings({ session_auto_send_context: !settings.session_auto_send_context });
  }, [updateSettings, settings.session_auto_send_context]);

  const refetch = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);

      const response = await makeApiCall('/api/v1/member/session-settings/');
      
      if (!response.ok) {
        throw new Error(`Failed to fetch session settings: ${response.status}`);
      }
      
      const data: SessionSettings = await response.json();
      setSettings(data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch session settings';
      setError(errorMessage);
      console.error('Error fetching session settings:', err);
    } finally {
      setIsLoading(false);
    }
  }, [makeApiCall]);

  return {
    settings,
    isLoading,
    error,
    isUpdating,
    updateSettings,
    toggleAutoSendContext,
    refetch
  };
}