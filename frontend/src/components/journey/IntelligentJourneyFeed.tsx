'use client';

import React, { useState, useCallback, useRef, useEffect } from 'react';
import { useAdvancedInsights, AdvancedInsightsFilters } from '@/hooks/journey/useAdvancedInsights';
import { SmartFilterBar } from './SmartFilterBar';
import { InsightCard } from './InsightCard';
import { JourneyFeedSkeletons } from './JourneyFeedSkeletons';
import { EmptyState } from './EmptyState';
import { Button } from '@/components/ui/button';
import { Alert } from '@/components/ui/alert';

interface IntelligentJourneyFeedProps {
  className?: string;
  initialFilters?: AdvancedInsightsFilters;
}

export function IntelligentJourneyFeed({ 
  className = '', 
  initialFilters = {} 
}: IntelligentJourneyFeedProps) {
  const [activeFilters, setActiveFilters] = useState<AdvancedInsightsFilters>(initialFilters);
  const loadMoreRef = useRef<HTMLDivElement>(null);
  
  const {
    insights,
    loading,
    error,
    hasMore,
    loadMore,
    totalCount,
    facets,
    refresh,
    isRefreshing
  } = useAdvancedInsights(activeFilters);

  // Handle filter changes
  const handleFiltersChange = useCallback((newFilters: AdvancedInsightsFilters) => {
    setActiveFilters(newFilters);
  }, []);

  // Infinite scroll implementation
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        const target = entries[0];
        if (target.isIntersecting && hasMore && !loading) {
          loadMore();
        }
      },
      {
        threshold: 0.1,
        rootMargin: '100px'
      }
    );

    const currentRef = loadMoreRef.current;
    if (currentRef) {
      observer.observe(currentRef);
    }

    return () => {
      if (currentRef) {
        observer.unobserve(currentRef);
      }
    };
  }, [hasMore, loading, loadMore]);

  // Generate filter suggestions based on facets
  const getFilterSuggestions = useCallback(() => {
    if (!facets) return [];
    
    const suggestions = [];
    
    // Suggest popular categories
    const topCategories = Object.entries(facets.categories)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 3)
      .filter(([category]) => !activeFilters.categories?.includes(category));
    
    suggestions.push(...topCategories.map(([category, count]) => ({
      type: 'category' as const,
      label: category,
      count,
      filter: { categories: [...(activeFilters.categories || []), category] }
    })));

    // Suggest popular tags
    const topTags = Object.entries(facets.tags)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 3)
      .filter(([tag]) => !activeFilters.tags?.includes(tag));
    
    suggestions.push(...topTags.map(([tag, count]) => ({
      type: 'tag' as const,
      label: tag,
      count,
      filter: { tags: [...(activeFilters.tags || []), tag] }
    })));

    return suggestions.slice(0, 5); // Limit to 5 suggestions
  }, [facets, activeFilters]);

  const suggestions = getFilterSuggestions();

  // Handle retry on error
  const handleRetry = useCallback(() => {
    refresh();
  }, [refresh]);

  return (
    <div className={`w-full ${className}`}>
      {/* Filter Bar */}
      <div className="sticky top-0 z-10 bg-background/95 backdrop-blur-sm border-b border-border mb-6">
        <div className="py-4">
          <SmartFilterBar
            filters={activeFilters}
            onFiltersChange={handleFiltersChange}
            suggestions={suggestions}
            facets={facets}
            totalCount={totalCount}
            isLoading={loading && insights.length === 0}
          />
        </div>
      </div>

      {/* Error State */}
      {error && (
        <Alert className="mb-6 border-destructive/50 text-destructive">
          <div className="flex items-center justify-between">
            <div>
              <h4 className="font-semibold">Error loading insights</h4>
              <p className="text-sm mt-1">{error}</p>
            </div>
            <Button 
              variant="outline" 
              size="sm" 
              onClick={handleRetry}
              disabled={isRefreshing}
            >
              {isRefreshing ? 'Retrying...' : 'Retry'}
            </Button>
          </div>
        </Alert>
      )}

      {/* Loading State - Initial Load */}
      {loading && insights.length === 0 && !error && (
        <JourneyFeedSkeletons count={6} />
      )}

      {/* Empty State */}
      {!loading && insights.length === 0 && !error && (
        <EmptyState 
          filters={activeFilters}
          onClearFilters={() => setActiveFilters({})}
          onRefresh={refresh}
        />
      )}

      {/* Feed Content */}
      {insights.length > 0 && (
        <div className="space-y-4">
          {/* Results Summary */}
          <div className="flex items-center justify-between text-sm text-muted-foreground mb-4">
            <span>
              Showing {insights.length} of {totalCount} insights
            </span>
            {isRefreshing && (
              <span className="flex items-center gap-2">
                <div className="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin" />
                Refreshing...
              </span>
            )}
          </div>

          {/* Insight Cards */}
          <div className="grid gap-4">
            {insights.map((insight, index) => (
              <InsightCard
                key={`${insight.id}-${index}`}
                insight={insight}
                className="transition-all duration-200 hover:shadow-md"
              />
            ))}
          </div>

          {/* Load More Trigger */}
          <div ref={loadMoreRef} className="py-8">
            {loading && insights.length > 0 && (
              <div className="flex justify-center">
                <div className="flex items-center gap-2 text-muted-foreground">
                  <div className="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin" />
                  Loading more insights...
                </div>
              </div>
            )}
            
            {!hasMore && insights.length > 0 && (
              <div className="text-center text-muted-foreground">
                <p>You've reached the end of your insights.</p>
                <Button 
                  variant="ghost" 
                  size="sm" 
                  onClick={refresh}
                  className="mt-2"
                  disabled={isRefreshing}
                >
                  Refresh feed
                </Button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}