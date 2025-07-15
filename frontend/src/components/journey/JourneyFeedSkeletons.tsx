'use client';

import React from 'react';
import { Card, CardHeader, CardContent, CardFooter } from '@/components/ui/card';

interface JourneyFeedSkeletonsProps {
  count?: number;
  className?: string;
}

function SkeletonLine({ width = 'w-full', height = 'h-4' }: { width?: string; height?: string }) {
  return (
    <div className={`${width} ${height} bg-muted rounded animate-pulse`} />
  );
}

function SkeletonCircle({ size = 'w-4 h-4' }: { size?: string }) {
  return (
    <div className={`${size} bg-muted rounded-full animate-pulse`} />
  );
}

function InsightCardSkeleton() {
  return (
    <Card className="animate-pulse">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex-1 space-y-3">
            {/* Title with icon */}
            <div className="flex items-center gap-2">
              <SkeletonCircle size="w-5 h-5" />
              <SkeletonLine width="w-3/4" height="h-5" />
            </div>
            
            {/* Metadata row */}
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-1">
                <SkeletonCircle size="w-4 h-4" />
                <SkeletonLine width="w-20" height="h-3" />
              </div>
              <div className="flex items-center gap-1">
                <SkeletonCircle size="w-4 h-4" />
                <SkeletonLine width="w-16" height="h-3" />
              </div>
              <div className="flex items-center gap-1">
                <SkeletonCircle size="w-4 h-4" />
                <SkeletonLine width="w-12" height="h-3" />
              </div>
            </div>
          </div>
          
          {/* Action buttons */}
          <div className="flex items-center gap-2">
            <SkeletonCircle size="w-8 h-8" />
            <SkeletonCircle size="w-8 h-8" />
          </div>
        </div>

        {/* Badges */}
        <div className="flex flex-wrap gap-2 mt-3">
          <SkeletonLine width="w-16" height="h-5" />
          <SkeletonLine width="w-20" height="h-5" />
          <SkeletonLine width="w-14" height="h-5" />
        </div>
      </CardHeader>

      <CardContent>
        <div className="space-y-3">
          {/* Summary text */}
          <div className="space-y-2">
            <SkeletonLine width="w-full" height="h-4" />
            <SkeletonLine width="w-full" height="h-4" />
            <SkeletonLine width="w-3/4" height="h-4" />
          </div>

          {/* Tags */}
          <div className="flex flex-wrap gap-1 mt-4">
            <SkeletonLine width="w-12" height="h-5" />
            <SkeletonLine width="w-16" height="h-5" />
            <SkeletonLine width="w-14" height="h-5" />
            <SkeletonLine width="w-18" height="h-5" />
          </div>
        </div>
      </CardContent>

      <CardFooter className="flex items-center justify-between">
        {/* Expand button */}
        <div className="flex items-center gap-1">
          <SkeletonCircle size="w-4 h-4" />
          <SkeletonLine width="w-20" height="h-4" />
        </div>

        {/* Rating buttons */}
        <div className="flex items-center gap-1">
          <SkeletonLine width="w-16" height="h-3" />
          <SkeletonCircle size="w-6 h-6" />
          <SkeletonCircle size="w-6 h-6" />
        </div>
      </CardFooter>
    </Card>
  );
}

function FilterBarSkeleton() {
  return (
    <div className="space-y-4 animate-pulse">
      {/* Main filter row */}
      <div className="flex flex-wrap items-center gap-3">
        {/* Search input */}
        <div className="flex-1 min-w-[200px]">
          <SkeletonLine width="w-full" height="h-9" />
        </div>
        
        {/* Sort dropdown */}
        <SkeletonLine width="w-32" height="h-9" />
        
        {/* Filter button */}
        <SkeletonLine width="w-20" height="h-9" />
        
        {/* Clear button */}
        <SkeletonLine width="w-16" height="h-9" />
      </div>

      {/* Active filters */}
      <div className="flex flex-wrap items-center gap-2">
        <SkeletonLine width="w-20" height="h-3" />
        <SkeletonLine width="w-24" height="h-6" />
        <SkeletonLine width="w-28" height="h-6" />
        <SkeletonLine width="w-20" height="h-6" />
      </div>

      {/* Suggestions */}
      <div className="space-y-2">
        <SkeletonLine width="w-32" height="h-3" />
        <div className="flex flex-wrap gap-2">
          <SkeletonLine width="w-20" height="h-7" />
          <SkeletonLine width="w-24" height="h-7" />
          <SkeletonLine width="w-28" height="h-7" />
          <SkeletonLine width="w-22" height="h-7" />
        </div>
      </div>

      {/* Results summary */}
      <div className="flex items-center justify-between">
        <SkeletonLine width="w-32" height="h-3" />
        <SkeletonLine width="w-24" height="h-3" />
      </div>
    </div>
  );
}

export function JourneyFeedSkeletons({ count = 6, className = '' }: JourneyFeedSkeletonsProps) {
  return (
    <div className={`w-full ${className}`}>
      {/* Filter bar skeleton */}
      <div className="sticky top-0 z-10 bg-background/95 backdrop-blur-sm border-b border-border mb-6">
        <div className="py-4">
          <FilterBarSkeleton />
        </div>
      </div>

      {/* Feed skeletons */}
      <div className="space-y-4">
        {/* Results summary skeleton */}
        <div className="flex items-center justify-between mb-4">
          <SkeletonLine width="w-40" height="h-4" />
        </div>

        {/* Card skeletons */}
        <div className="grid gap-4">
          {Array.from({ length: count }, (_, index) => (
            <InsightCardSkeleton key={index} />
          ))}
        </div>
      </div>
    </div>
  );
}

// Individual skeleton components for more granular use
export function InsightCardSkeletonOnly() {
  return <InsightCardSkeleton />;
}

export function FilterBarSkeletonOnly() {
  return <FilterBarSkeleton />;
}

// Compact skeleton for loading more items
export function CompactInsightSkeleton() {
  return (
    <Card className="animate-pulse">
      <CardHeader className="pb-3">
        <div className="flex items-center gap-2">
          <SkeletonCircle size="w-4 h-4" />
          <SkeletonLine width="w-2/3" height="h-4" />
        </div>
        <div className="flex gap-2 mt-2">
          <SkeletonLine width="w-12" height="h-4" />
          <SkeletonLine width="w-16" height="h-4" />
        </div>
      </CardHeader>
      <CardContent className="pt-0">
        <div className="space-y-2">
          <SkeletonLine width="w-full" height="h-3" />
          <SkeletonLine width="w-4/5" height="h-3" />
        </div>
      </CardContent>
    </Card>
  );
}

// Loading more indicator
export function LoadingMoreSkeleton() {
  return (
    <div className="flex justify-center py-8">
      <div className="flex items-center gap-2 text-muted-foreground">
        <div className="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin" />
        <SkeletonLine width="w-32" height="h-4" />
      </div>
    </div>
  );
}