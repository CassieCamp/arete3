'use client';

import { useState, useEffect, useCallback } from 'react';
import { useApiClient } from '@/utils/api';

interface UseJourneyFeedParams {
  categories?: string[];
  limit?: number;
  skip?: number;
}

// NOTE: The Insight type might need to be imported from a models/types file if one exists.
// For now, `any` is a placeholder.
interface JourneyFeedData {
  insights: any[]; // Use existing Insight type if available
  categoryCounts: Record<string, number>;
  totalCount: number;
  hasMore: boolean;
}

interface UseJourneyFeedReturn {
  data: JourneyFeedData | null;
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

export const useJourneyFeed = (params: UseJourneyFeedParams = {}): UseJourneyFeedReturn => {
  const [data, setData] = useState<JourneyFeedData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const { makeApiCall } = useApiClient();

  const fetchFeed = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const queryParams = new URLSearchParams({
        limit: (params.limit || 20).toString(),
        skip: (params.skip || 0).toString(),
      });
      
      if (params.categories?.length) {
        params.categories.forEach(cat => queryParams.append('categories', cat));
      }

      const response = await makeApiCall(`/api/v1/journey/feed?${queryParams}`);
      
      if (response.ok) {
        const feedData = await response.json();
        setData(feedData);
      } else {
        throw new Error(`Failed to fetch journey feed: ${response.status}`);
      }
    } catch (err) {
      console.error('Journey feed error:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch journey feed');
    } finally {
      setLoading(false);
    }
  }, [params.categories, params.limit, params.skip, makeApiCall]);

  useEffect(() => {
    fetchFeed();
  }, [fetchFeed]);

  return { 
    data, 
    loading, 
    error, 
    refetch: fetchFeed 
  };
};