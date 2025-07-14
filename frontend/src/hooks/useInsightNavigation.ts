import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { sessionInsightService, SessionInsight } from '@/services/sessionInsightService';
import { useEntryService, Entry } from '@/services/entryService';
import { useAuth as useClerkAuth, useUser } from '@clerk/nextjs';

export interface UseInsightNavigationResult {
  insights: SessionInsight[];
  currentIndex: number;
  currentInsight: SessionInsight | null;
  loading: boolean;
  error: string | null;
  hasNext: boolean;
  hasPrevious: boolean;
  navigateToNext: () => void;
  navigateToPrevious: () => void;
  navigateToIndex: (index: number) => void;
  totalCount: number;
}

export function useInsightNavigation(currentInsightId: string): UseInsightNavigationResult {
  const [insights, setInsights] = useState<SessionInsight[]>([]);
  const [currentIndex, setCurrentIndex] = useState(-1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { isSignedIn, getToken } = useClerkAuth();
  const { isLoaded } = useUser();
  const router = useRouter();
  const entryService = useEntryService();

  const getAuthToken = async (): Promise<string | null> => {
    if (!isSignedIn) return null;
    try {
      return await getToken();
    } catch (error) {
      console.error('Failed to get auth token:', error);
      return null;
    }
  };

  const fetchAllInsights = useCallback(async () => {
    if (!currentInsightId) {
      setError('No insight ID provided');
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);

      // Wait for Clerk to be loaded
      if (!isLoaded) {
        let waitCount = 0;
        while (!isLoaded && waitCount < 10) {
          await new Promise(resolve => setTimeout(resolve, 500));
          waitCount++;
        }
      }

      if (!isSignedIn) {
        throw new Error('User is not signed in');
      }

      // Get authentication token with retry logic
      let token = await getAuthToken();
      let retryCount = 0;
      const maxRetries = 5;

      while (!token && retryCount < maxRetries) {
        await new Promise(resolve => setTimeout(resolve, 1500));
        token = await getAuthToken();
        retryCount++;
      }

      if (!token) {
        throw new Error('No authentication token available');
      }

      // Fetch all entries that have insights
      // We'll use the entry service to get all entries, then filter for those with insights
      const entriesData = await entryService.getEntries({
        limit: 100, // Get a large number to ensure we get all insights
        offset: 0
      });

      // Filter entries that have insights and convert to SessionInsight format
      const entriesWithInsights = entriesData.entries.filter(entry => entry.has_insights);
      
      // Convert entries to SessionInsight format for navigation
      const insightList: SessionInsight[] = entriesWithInsights.map(entry => ({
        id: entry.id,
        client_user_id: '', // Will be populated when individual insight is loaded
        session_date: entry.session_date || entry.created_at,
        session_title: entry.title,
        key_themes: [], // Will be populated when individual insight is loaded
        status: 'completed',
        created_at: entry.created_at,
        title: entry.title,
        content: entry.content
      }));

      // Sort by date (newest first)
      insightList.sort((a, b) => {
        const dateA = new Date(a.session_date || a.created_at);
        const dateB = new Date(b.session_date || b.created_at);
        return dateB.getTime() - dateA.getTime();
      });

      setInsights(insightList);

      // Find current insight index
      const currentIdx = insightList.findIndex(insight => insight.id === currentInsightId);
      setCurrentIndex(currentIdx);

      if (currentIdx === -1) {
        console.warn('Current insight not found in the list');
      }

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch insights';
      setError(errorMessage);
      console.error('Error fetching insights for navigation:', err);
    } finally {
      setLoading(false);
    }
  }, [currentInsightId, getAuthToken, isLoaded, isSignedIn, entryService]);

  useEffect(() => {
    fetchAllInsights();
  }, [fetchAllInsights]);

  const navigateToNext = useCallback(() => {
    if (currentIndex < insights.length - 1) {
      const nextIndex = currentIndex + 1;
      const nextInsight = insights[nextIndex];
      router.push(`/insights/${nextInsight.id}`);
    }
  }, [currentIndex, insights, router]);

  const navigateToPrevious = useCallback(() => {
    if (currentIndex > 0) {
      const prevIndex = currentIndex - 1;
      const prevInsight = insights[prevIndex];
      router.push(`/insights/${prevInsight.id}`);
    }
  }, [currentIndex, insights, router]);

  const navigateToIndex = useCallback((index: number) => {
    if (index >= 0 && index < insights.length) {
      const targetInsight = insights[index];
      router.push(`/insights/${targetInsight.id}`);
    }
  }, [insights, router]);

  const currentInsight = currentIndex >= 0 ? insights[currentIndex] : null;
  const hasNext = currentIndex < insights.length - 1;
  const hasPrevious = currentIndex > 0;

  return {
    insights,
    currentIndex,
    currentInsight,
    loading,
    error,
    hasNext,
    hasPrevious,
    navigateToNext,
    navigateToPrevious,
    navigateToIndex,
    totalCount: insights.length
  };
}