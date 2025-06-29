"use client";

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { LucideIcon, MoreHorizontal, RefreshCw } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface DashboardWidgetProps {
  title: string;
  description?: string;
  icon?: LucideIcon;
  children: React.ReactNode;
  className?: string;
  loading?: boolean;
  error?: string;
  onRefresh?: () => void;
  actions?: React.ReactNode;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  variant?: 'default' | 'outline' | 'secondary';
}

export function DashboardWidget({
  title,
  description,
  icon: Icon,
  children,
  className,
  loading = false,
  error,
  onRefresh,
  actions,
  size = 'md',
  variant = 'default'
}: DashboardWidgetProps) {
  const sizeClasses = {
    sm: 'col-span-1',
    md: 'col-span-1 md:col-span-2',
    lg: 'col-span-1 md:col-span-2 lg:col-span-3',
    xl: 'col-span-1 md:col-span-2 lg:col-span-4'
  };

  const variantClasses = {
    default: '',
    outline: 'border-2',
    secondary: 'bg-secondary'
  };

  return (
    <Card className={cn(
      sizeClasses[size],
      variantClasses[variant],
      'transition-all duration-200 hover:shadow-md',
      className
    )}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <div className="flex items-center space-x-2">
          {Icon && (
            <div className="p-2 rounded-lg bg-primary/10">
              <Icon className="h-4 w-4 text-primary" />
            </div>
          )}
          <div>
            <CardTitle className="text-sm font-medium">{title}</CardTitle>
            {description && (
              <CardDescription className="text-xs">{description}</CardDescription>
            )}
          </div>
        </div>
        
        <div className="flex items-center space-x-1">
          {onRefresh && (
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8"
              onClick={onRefresh}
              disabled={loading}
            >
              <RefreshCw className={cn(
                "h-4 w-4",
                loading && "animate-spin"
              )} />
            </Button>
          )}
          {actions}
        </div>
      </CardHeader>
      
      <CardContent>
        {error ? (
          <div className="flex flex-col items-center justify-center py-8 text-center">
            <div className="text-destructive text-sm mb-2">Error loading data</div>
            <div className="text-xs text-muted-foreground mb-4">{error}</div>
            {onRefresh && (
              <Button variant="outline" size="sm" onClick={onRefresh}>
                Try Again
              </Button>
            )}
          </div>
        ) : loading ? (
          <div className="flex items-center justify-center py-8">
            <div className="flex items-center space-x-2">
              <RefreshCw className="h-4 w-4 animate-spin" />
              <span className="text-sm text-muted-foreground">Loading...</span>
            </div>
          </div>
        ) : (
          children
        )}
      </CardContent>
    </Card>
  );
}

// Skeleton component for loading states
export function DashboardWidgetSkeleton({ 
  size = 'md',
  className 
}: { 
  size?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
}) {
  const sizeClasses = {
    sm: 'col-span-1',
    md: 'col-span-1 md:col-span-2',
    lg: 'col-span-1 md:col-span-2 lg:col-span-3',
    xl: 'col-span-1 md:col-span-2 lg:col-span-4'
  };

  return (
    <Card className={cn(sizeClasses[size], className)}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <div className="flex items-center space-x-2">
          <div className="h-8 w-8 bg-muted animate-pulse rounded-lg" />
          <div>
            <div className="h-4 w-24 bg-muted animate-pulse rounded" />
            <div className="h-3 w-32 bg-muted animate-pulse rounded mt-1" />
          </div>
        </div>
        <div className="h-8 w-8 bg-muted animate-pulse rounded" />
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          <div className="h-4 w-full bg-muted animate-pulse rounded" />
          <div className="h-4 w-3/4 bg-muted animate-pulse rounded" />
          <div className="h-4 w-1/2 bg-muted animate-pulse rounded" />
        </div>
      </CardContent>
    </Card>
  );
}

// Metric display component for widgets
export interface MetricProps {
  label: string;
  value: string | number;
  change?: {
    value: number;
    type: 'increase' | 'decrease' | 'neutral';
  };
  icon?: LucideIcon;
  className?: string;
}

export function Metric({ 
  label, 
  value, 
  change, 
  icon: Icon,
  className 
}: MetricProps) {
  const getChangeColor = (type: 'increase' | 'decrease' | 'neutral') => {
    switch (type) {
      case 'increase':
        return 'text-green-600';
      case 'decrease':
        return 'text-red-600';
      case 'neutral':
        return 'text-muted-foreground';
    }
  };

  const getChangeSymbol = (type: 'increase' | 'decrease' | 'neutral') => {
    switch (type) {
      case 'increase':
        return '+';
      case 'decrease':
        return '-';
      case 'neutral':
        return '';
    }
  };

  return (
    <div className={cn("space-y-1", className)}>
      <div className="flex items-center justify-between">
        <span className="text-sm text-muted-foreground">{label}</span>
        {Icon && <Icon className="h-4 w-4 text-muted-foreground" />}
      </div>
      <div className="flex items-baseline space-x-2">
        <span className="text-2xl font-bold">{value}</span>
        {change && (
          <span className={cn(
            "text-xs font-medium",
            getChangeColor(change.type)
          )}>
            {getChangeSymbol(change.type)}{Math.abs(change.value)}%
          </span>
        )}
      </div>
    </div>
  );
}