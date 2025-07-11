import { useState, useEffect } from 'react';
import { sessionInsightService, SessionInsightDetail } from '@/services/sessionInsightService';
import { useAuth } from '@/context/AuthContext';
import { useAuth as useClerkAuth } from '@clerk/nextjs';

interface UseSessionInsightResult {
  insight: SessionInsightDetail | null;
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

export function useSessionInsight(insightId: string): UseSessionInsightResult {
  const [insight, setInsight] = useState<SessionInsightDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { getAuthToken } = useAuth();
  const { isSignedIn, isLoaded } = useClerkAuth();

  const fetchInsight = async () => {
    if (!insightId) {
      setError('No insight ID provided');
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      console.log('🔍 Starting fetchInsight for ID:', insightId);
      console.log('🔍 Clerk state - isLoaded:', isLoaded, 'isSignedIn:', isSignedIn);
      
      // Wait for Clerk to be loaded first
      if (!isLoaded) {
        console.log('⏳ Waiting for Clerk to load...');
        let waitCount = 0;
        while (!isLoaded && waitCount < 10) {
          await new Promise(resolve => setTimeout(resolve, 500));
          waitCount++;
        }
        console.log('✅ Clerk loaded after', waitCount * 500, 'ms');
      }
      
      if (!isSignedIn) {
        throw new Error('User is not signed in to Clerk');
      }
      
      // Add retry logic for authentication token
      let token = await getAuthToken();
      let retryCount = 0;
      const maxRetries = 5; // Increased retries
      
      while (!token && retryCount < maxRetries) {
        console.log(`Authentication token not available, retrying... (${retryCount + 1}/${maxRetries})`);
        await new Promise(resolve => setTimeout(resolve, 1500)); // Increased wait time
        token = await getAuthToken();
        retryCount++;
      }
      
      if (!token) {
        throw new Error('No authentication token available after retries');
      }

      console.log('✅ Got authentication token, making API call...');
      const data = await sessionInsightService.getSessionInsightDetail(token, insightId);
      console.log('✅ Successfully fetched session insight data');
      setInsight(data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch session insight';
      setError(errorMessage);
      console.error('❌ Error fetching session insight:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInsight();
  }, [insightId]);

  const refetch = async () => {
    await fetchInsight();
  };

  return {
    insight,
    loading,
    error,
    refetch
  };
}