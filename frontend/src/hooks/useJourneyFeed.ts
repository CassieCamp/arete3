import { useState, useEffect, useCallback } from 'react';

// Assume Insight type is defined elsewhere, e.g., in 'types/journey.ts' (see below for file content)
// import { Insight } from ''types/journey'' (see below for file content); 
// For now, we'll use a placeholder
interface Insight {
  id: string;
  summary: string;
  created_at: string;
  reflection?: { type: string };
  categories: string[];
  key_points?: string[];
  breakthrough_moment?: string;
  confidence_score: number;
  action_items?: any[];
}

// Assume getAuthToken is defined elsewhere, e.g., in 'lib/auth.ts' (see below for file content)
const getAuthToken = () => {
  // Placeholder for getting the auth token, e.g., from Clerk
  return 'DUMMY_TOKEN';
};

interface JourneyFeedParams {
  categories?: string[];
  limit?: number;
  skip?: number;
}

interface JourneyFeedData {
  insights: Insight[];
  categoryCounts: Record<string, number>;
  totalCount: number;
  hasMore: boolean;
}

export const useJourneyFeed = (params: JourneyFeedParams = {}) => {
  const [data, setData] = useState<JourneyFeedData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

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

      const response = await fetch(`/api/v1/journey/feed?${queryParams}`, {
        headers: { 'Authorization': `Bearer ${getAuthToken()}` }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch journey feed');
      }

      const feedData = await response.json();
      setData(feedData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }, [params.categories, params.limit, params.skip]);

  useEffect(() => {
    fetchFeed();
  }, [fetchFeed]);

  return { data, loading, error, refetch: fetchFeed };
};