"use client";

import React, { useState, useEffect } from 'react';
import { DashboardWidget, Metric } from './DashboardWidget';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { 
  TrendingUp, 
  TrendingDown, 
  Target, 
  Brain, 
  Users, 
  Calendar,
  Award,
  Clock,
  BarChart3
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface ProgressData {
  goals: {
    total: number;
    completed: number;
    active: number;
    completionRate: number;
  };
  insights: {
    total: number;
    thisMonth: number;
    trend: 'up' | 'down' | 'stable';
    trendValue: number;
  };
  relationships: {
    total: number;
    active: number;
    healthScore: number;
  };
  sessions: {
    thisMonth: number;
    lastMonth: number;
    trend: 'up' | 'down' | 'stable';
  };
  overallProgress: number;
  streakDays: number;
}

interface ProgressOverviewWidgetProps {
  userRole: 'coach' | 'client';
  userId?: string;
  className?: string;
  compact?: boolean;
}

export function ProgressOverviewWidget({
  userRole,
  userId,
  className,
  compact = false
}: ProgressOverviewWidgetProps) {
  const [data, setData] = useState<ProgressData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchProgressData();
  }, [userId, userRole]);

  const fetchProgressData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Simulate API call - replace with actual API endpoint
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Mock data based on user role
      const mockData: ProgressData = userRole === 'coach' ? {
        goals: { total: 24, completed: 18, active: 6, completionRate: 75 },
        insights: { total: 156, thisMonth: 23, trend: 'up', trendValue: 15 },
        relationships: { total: 8, active: 7, healthScore: 92 },
        sessions: { thisMonth: 32, lastMonth: 28, trend: 'up' },
        overallProgress: 87,
        streakDays: 12
      } : {
        goals: { total: 8, completed: 5, active: 3, completionRate: 62.5 },
        insights: { total: 42, thisMonth: 8, trend: 'up', trendValue: 12 },
        relationships: { total: 1, active: 1, healthScore: 95 },
        sessions: { thisMonth: 6, lastMonth: 4, trend: 'up' },
        overallProgress: 73,
        streakDays: 5
      };
      
      setData(mockData);
    } catch (err) {
      setError('Failed to load progress data');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = () => {
    fetchProgressData();
  };

  if (compact && data) {
    return (
      <DashboardWidget
        title="Progress Overview"
        description="Your coaching journey"
        icon={BarChart3}
        onRefresh={handleRefresh}
        loading={loading}
        error={error || undefined}
        size="md"
        className={className}
      >
        <CompactProgressView data={data} userRole={userRole} />
      </DashboardWidget>
    );
  }

  return (
    <DashboardWidget
      title="Progress Overview"
      description={`${userRole === 'coach' ? 'Coaching' : 'Personal'} progress summary`}
      icon={BarChart3}
      onRefresh={handleRefresh}
      loading={loading}
      error={error || undefined}
      size="xl"
      className={className}
    >
      {data && <DetailedProgressView data={data} userRole={userRole} />}
    </DashboardWidget>
  );
}

function CompactProgressView({ 
  data, 
  userRole 
}: { 
  data: ProgressData; 
  userRole: 'coach' | 'client';
}) {
  return (
    <div className="space-y-4">
      {/* Overall Progress */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium">Overall Progress</span>
          <span className="text-sm text-muted-foreground">{data.overallProgress}%</span>
        </div>
        <Progress value={data.overallProgress} className="h-2" />
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-2 gap-4">
        <Metric
          label="Goals Completed"
          value={`${data.goals.completed}/${data.goals.total}`}
          change={{
            value: data.goals.completionRate,
            type: data.goals.completionRate > 50 ? 'increase' : 'decrease'
          }}
          icon={Target}
        />
        <Metric
          label={userRole === 'coach' ? 'Client Insights' : 'My Insights'}
          value={data.insights.thisMonth}
          change={{
            value: data.insights.trendValue,
            type: data.insights.trend === 'up' ? 'increase' : 'decrease'
          }}
          icon={Brain}
        />
      </div>
    </div>
  );
}

function DetailedProgressView({ 
  data, 
  userRole 
}: { 
  data: ProgressData; 
  userRole: 'coach' | 'client';
}) {
  return (
    <div className="space-y-6">
      {/* Overall Progress Bar */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold">Overall Progress</h3>
          <div className="flex items-center space-x-2">
            <Award className="h-4 w-4 text-yellow-500" />
            <span className="text-sm font-medium">{data.streakDays} day streak</span>
          </div>
        </div>
        <div className="space-y-2">
          <Progress value={data.overallProgress} className="h-3" />
          <div className="flex justify-between text-xs text-muted-foreground">
            <span>Getting started</span>
            <span className="font-medium">{data.overallProgress}% complete</span>
            <span>Expert level</span>
          </div>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Goals"
          value={data.goals.completed}
          subtitle={`of ${data.goals.total} completed`}
          icon={Target}
          progress={data.goals.completionRate}
          trend={{
            value: data.goals.completionRate,
            type: data.goals.completionRate > 50 ? 'increase' : 'decrease'
          }}
        />
        
        <MetricCard
          title="Insights"
          value={data.insights.thisMonth}
          subtitle="this month"
          icon={Brain}
          trend={{
            value: data.insights.trendValue,
            type: data.insights.trend === 'up' ? 'increase' : 'decrease'
          }}
        />
        
        <MetricCard
          title={userRole === 'coach' ? 'Clients' : 'Coaches'}
          value={data.relationships.active}
          subtitle={`of ${data.relationships.total} active`}
          icon={Users}
          progress={data.relationships.healthScore}
          trend={{
            value: data.relationships.healthScore,
            type: data.relationships.healthScore > 80 ? 'increase' : 'neutral'
          }}
        />
        
        <MetricCard
          title="Sessions"
          value={data.sessions.thisMonth}
          subtitle="this month"
          icon={Calendar}
          trend={{
            value: Math.abs(data.sessions.thisMonth - data.sessions.lastMonth),
            type: data.sessions.thisMonth > data.sessions.lastMonth ? 'increase' : 'decrease'
          }}
        />
      </div>

      {/* Recent Activity Summary */}
      <div className="space-y-3">
        <h3 className="font-semibold">Recent Activity</h3>
        <div className="space-y-2">
          <ActivityItem
            icon={Target}
            text={`${data.goals.active} active goals in progress`}
            time="Updated today"
          />
          <ActivityItem
            icon={Brain}
            text={`${data.insights.thisMonth} insights generated this month`}
            time="Last insight 2 days ago"
          />
          <ActivityItem
            icon={Users}
            text={`${data.relationships.active} active ${userRole === 'coach' ? 'client' : 'coaching'} relationships`}
            time="All connections healthy"
          />
        </div>
      </div>
    </div>
  );
}

interface MetricCardProps {
  title: string;
  value: number;
  subtitle: string;
  icon: React.ComponentType<{ className?: string }>;
  progress?: number;
  trend?: {
    value: number;
    type: 'increase' | 'decrease' | 'neutral';
  };
}

function MetricCard({ title, value, subtitle, icon: Icon, progress, trend }: MetricCardProps) {
  const getTrendIcon = () => {
    if (!trend) return null;
    return trend.type === 'increase' ? TrendingUp : 
           trend.type === 'decrease' ? TrendingDown : null;
  };

  const getTrendColor = () => {
    if (!trend) return '';
    return trend.type === 'increase' ? 'text-green-600' : 
           trend.type === 'decrease' ? 'text-red-600' : 'text-muted-foreground';
  };

  const TrendIcon = getTrendIcon();

  return (
    <div className="p-4 rounded-lg border bg-card">
      <div className="flex items-center justify-between mb-2">
        <Icon className="h-4 w-4 text-muted-foreground" />
        {TrendIcon && (
          <div className={cn("flex items-center space-x-1", getTrendColor())}>
            <TrendIcon className="h-3 w-3" />
            <span className="text-xs font-medium">{trend?.value}%</span>
          </div>
        )}
      </div>
      <div className="space-y-1">
        <div className="text-2xl font-bold">{value}</div>
        <div className="text-xs text-muted-foreground">{subtitle}</div>
        <div className="text-xs font-medium text-muted-foreground">{title}</div>
      </div>
      {progress !== undefined && (
        <div className="mt-3">
          <Progress value={progress} className="h-1" />
        </div>
      )}
    </div>
  );
}

interface ActivityItemProps {
  icon: React.ComponentType<{ className?: string }>;
  text: string;
  time: string;
}

function ActivityItem({ icon: Icon, text, time }: ActivityItemProps) {
  return (
    <div className="flex items-center space-x-3 p-2 rounded-lg hover:bg-accent/50 transition-colors">
      <div className="p-1.5 rounded bg-primary/10">
        <Icon className="h-3 w-3 text-primary" />
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm">{text}</p>
        <p className="text-xs text-muted-foreground">{time}</p>
      </div>
    </div>
  );
}