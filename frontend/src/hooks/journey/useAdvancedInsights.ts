import { useState, useEffect, useCallback, useRef } from 'react';

// Types based on backend schemas
export interface InsightItem {
  type: 'insight';
  id: string;
  title: string;
  content: string;
  summary?: string;
  category: string;
  subcategories?: string[];
  tags: string[];
  source_id: string;
  source_title?: string;
  source_excerpt?: string;
  review_status: string;
  confidence_score?: number;
  is_favorite: boolean;
  is_actionable: boolean;
  suggested_actions?: string[];
  user_rating?: number;
  view_count: number;
  created_at: string;
  updated_at: string;
  generated_at: string;
}

export interface ReflectionItem {
  type: 'reflection';
  id: string;
  title: string;
  content?: string;
  description?: string;
  categories: string[];
  tags: string[];
  processing_status: string;
  insight_count: number;
  created_at: string;
  updated_at: string;
}

export type JourneyFeedItem = InsightItem | ReflectionItem;

export interface JourneyFeedResponse {
  items: JourneyFeedItem[];
  total_count: number;
  skip: number;
  limit: number;
  facets?: {
    categories: { [key: string]: number };
    tags: { [key: string]: number };
    review_statuses: { [key: string]: number };
    processing_statuses: { [key: string]: number };
  };
}

export interface AdvancedInsightsFilters {
  categories?: string[];
  timeRange?: {
    start?: string;
    end?: string;
  };
  searchQuery?: string;
  sortBy?: 'created_at' | 'updated_at' | 'generated_at' | 'confidence_score' | 'user_rating' | 'view_count';
  sortOrder?: 'asc' | 'desc';
  minConfidence?: number;
  reviewStatus?: string[];
  processingStatus?: string[];
  itemTypes?: ('insight' | 'reflection')[];
  isFavorite?: boolean;
  isActionable?: boolean;
  tags?: string[];
  hasUserRating?: boolean;
  minUserRating?: number;
}

export interface UseAdvancedInsightsReturn {
  insights: JourneyFeedItem[];
  loading: boolean;
  error: string | null;
  hasMore: boolean;
  loadMore: () => Promise<void>;
  totalCount: number;
  facets?: {
    categories: { [key: string]: number };
    tags: { [key: string]: number };
    review_statuses: { [key: string]: number };
    processing_statuses: { [key: string]: number };
  };
  refresh: () => Promise<void>;
  isRefreshing: boolean;
}

const DEFAULT_LIMIT = 20;

export const useAdvancedInsights = (filters: AdvancedInsightsFilters = {}): UseAdvancedInsightsReturn => {
  const [insights, setInsights] = useState<JourneyFeedItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasMore, setHasMore] = useState(true);
  const [totalCount, setTotalCount] = useState(0);
  const [facets, setFacets] = useState<{
    categories: { [key: string]: number };
    tags: { [key: string]: number };
    review_statuses: { [key: string]: number };
    processing_statuses: { [key: string]: number };
  }>();

  // Track current offset for pagination
  const offsetRef = useRef(0);
  const isLoadingRef = useRef(false);
  const filtersRef = useRef(filters);

  // Update filters ref when filters change
  useEffect(() => {
    filtersRef.current = filters;
  }, [filters]);

  const buildQueryParams = useCallback((offset: number = 0, limit: number = DEFAULT_LIMIT) => {
    const params = new URLSearchParams();
    
    params.set('offset', offset.toString());
    params.set('limit', limit.toString());

    const currentFilters = filtersRef.current;

    // Add filter parameters
    if (currentFilters.categories?.length) {
      params.set('categories', currentFilters.categories.join(','));
    }

    if (currentFilters.timeRange?.start) {
      params.set('start_date', currentFilters.timeRange.start);
    }

    if (currentFilters.timeRange?.end) {
      params.set('end_date', currentFilters.timeRange.end);
    }

    if (currentFilters.searchQuery?.trim()) {
      params.set('search', currentFilters.searchQuery.trim());
    }

    if (currentFilters.sortBy) {
      params.set('sort_by', currentFilters.sortBy);
    }

    if (currentFilters.sortOrder) {
      params.set('sort_order', currentFilters.sortOrder);
    }

    if (currentFilters.minConfidence !== undefined) {
      params.set('min_confidence', currentFilters.minConfidence.toString());
    }

    if (currentFilters.reviewStatus?.length) {
      params.set('review_status', currentFilters.reviewStatus.join(','));
    }

    if (currentFilters.processingStatus?.length) {
      params.set('processing_status', currentFilters.processingStatus.join(','));
    }

    if (currentFilters.itemTypes?.length) {
      params.set('item_types', currentFilters.itemTypes.join(','));
    }

    if (currentFilters.isFavorite !== undefined) {
      params.set('is_favorite', currentFilters.isFavorite.toString());
    }

    if (currentFilters.isActionable !== undefined) {
      params.set('is_actionable', currentFilters.isActionable.toString());
    }

    if (currentFilters.tags?.length) {
      params.set('tags', currentFilters.tags.join(','));
    }

    if (currentFilters.hasUserRating !== undefined) {
      params.set('has_user_rating', currentFilters.hasUserRating.toString());
    }

    if (currentFilters.minUserRating !== undefined) {
      params.set('min_user_rating', currentFilters.minUserRating.toString());
    }

    return params.toString();
  }, []);

  const fetchInsights = useCallback(async (offset: number = 0, append: boolean = false) => {
    if (isLoadingRef.current) return;

    try {
      isLoadingRef.current = true;
      
      if (!append) {
        setLoading(true);
      }
      setError(null);

      const queryParams = buildQueryParams(offset);
      const response = await fetch(`/api/v1/journey/feed?${queryParams}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch insights: ${response.status} ${response.statusText}`);
      }

      const data: JourneyFeedResponse = await response.json();

      if (append) {
        setInsights(prev => [...prev, ...data.items]);
      } else {
        setInsights(data.items);
      }

      setTotalCount(data.total_count);
      setHasMore(data.items.length === DEFAULT_LIMIT && (offset + data.items.length) < data.total_count);
      
      if (data.facets) {
        setFacets(data.facets);
      }

      // Update offset for next load
      offsetRef.current = offset + data.items.length;

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An unknown error occurred';
      setError(errorMessage);
      console.error('Error fetching insights:', err);
    } finally {
      setLoading(false);
      setIsRefreshing(false);
      isLoadingRef.current = false;
    }
  }, [buildQueryParams]);

  const loadMore = useCallback(async () => {
    if (!hasMore || isLoadingRef.current) return;
    await fetchInsights(offsetRef.current, true);
  }, [hasMore, fetchInsights]);

  const refresh = useCallback(async () => {
    setIsRefreshing(true);
    offsetRef.current = 0;
    await fetchInsights(0, false);
  }, [fetchInsights]);

  // Reset and fetch when filters change
  useEffect(() => {
    offsetRef.current = 0;
    setInsights([]);
    setHasMore(true);
    fetchInsights(0, false);
  }, [
    filters.categories,
    filters.timeRange?.start,
    filters.timeRange?.end,
    filters.searchQuery,
    filters.sortBy,
    filters.sortOrder,
    filters.minConfidence,
    filters.reviewStatus,
    filters.processingStatus,
    filters.itemTypes,
    filters.isFavorite,
    filters.isActionable,
    filters.tags,
    filters.hasUserRating,
    filters.minUserRating,
    fetchInsights
  ]);

  return {
    insights,
    loading,
    error,
    hasMore,
    loadMore,
    totalCount,
    facets,
    refresh,
    isRefreshing,
  };
};