"use client";

import { useState, useEffect } from 'react';
import { useAuth } from '@/context/AuthContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { PageHeader } from '@/components/navigation/NavigationUtils';
import { QuickActionsWidget } from '@/components/dashboard/QuickActionsWidget';
import { ProgressOverviewWidget } from '@/components/dashboard/ProgressOverviewWidget';
import { DashboardWidget } from '@/components/dashboard/DashboardWidget';
import { OnboardingGuide } from '@/components/onboarding/OnboardingGuide';
import { Brain, Activity, TrendingUp, Calendar } from 'lucide-react';

interface DashboardData {
  overview: any;
  recent_activity: any[];
  client_progress?: any[];
  relationship_health?: any;
  goal_progress?: any;
  coaching_journey?: any;
}

export default function DashboardPage() {
  const { user, getAuthToken } = useAuth();
  const userRole = (user?.role as 'coach' | 'client') || 'client';
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (user) {
      fetchDashboardData();
    }
  }, [user]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const token = await getAuthToken();
      const response = await fetch('http://localhost:8000/api/v1/dashboard/analytics', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch dashboard data');
      }

      const result = await response.json();
      setDashboardData(result.data);
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      setError('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      {/* <OnboardingGuide /> */}
      <PageHeader />
      
      <div className="space-y-6">
        {/* Welcome Section */}
        <Card>
          <CardHeader>
            <CardTitle>Welcome back, {user?.firstName}!</CardTitle>
            <CardDescription>
              {userRole === 'coach'
                ? 'Manage your clients and track their progress with AI-enhanced insights.'
                : 'Continue your growth journey with personalized coaching and insights.'
              }
            </CardDescription>
          </CardHeader>
        </Card>

        {/* Dashboard Widgets Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Quick Actions Widget */}
          <QuickActionsWidget
            userRole={userRole}
            maxActions={4}
            className="lg:col-span-2"
          />

          {/* Progress Overview Widget */}
          <ProgressOverviewWidget
            userRole={userRole}
            compact={true}
            className="lg:col-span-2"
          />

          {/* Recent Activity Widget */}
          <DashboardWidget
            title="Recent Activity"
            description="Your latest coaching activities"
            icon={Activity}
            size="lg"
            className="lg:col-span-2"
          >
            <div className="space-y-3">
              <ActivityItem
                icon={Brain}
                title="New insight generated"
                description="AI analysis completed for recent session"
                time="2 hours ago"
              />
              <ActivityItem
                icon={TrendingUp}
                title="Goal progress updated"
                description="Made progress on communication skills"
                time="1 day ago"
              />
              <ActivityItem
                icon={Calendar}
                title="Session scheduled"
                description="Next coaching session booked"
                time="2 days ago"
              />
            </div>
          </DashboardWidget>

          {/* Upcoming Events Widget */}
          <DashboardWidget
            title="Upcoming"
            description="Your schedule"
            icon={Calendar}
            size="md"
            className="lg:col-span-2"
          >
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 rounded-lg border">
                <div>
                  <p className="font-medium text-sm">Coaching Session</p>
                  <p className="text-xs text-muted-foreground">
                    {userRole === 'coach' ? 'with Sarah Johnson' : 'with Coach Mike'}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium">Tomorrow</p>
                  <p className="text-xs text-muted-foreground">2:00 PM</p>
                </div>
              </div>
              <div className="flex items-center justify-between p-3 rounded-lg border">
                <div>
                  <p className="font-medium text-sm">Goal Review</p>
                  <p className="text-xs text-muted-foreground">Monthly check-in</p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium">Friday</p>
                  <p className="text-xs text-muted-foreground">10:00 AM</p>
                </div>
              </div>
            </div>
          </DashboardWidget>
        </div>

        {/* Full Progress Overview for larger screens */}
        <div className="hidden xl:block">
          <ProgressOverviewWidget
            userRole={userRole}
            compact={false}
          />
        </div>
      </div>
    </div>
  );
}

interface ActivityItemProps {
  icon: React.ComponentType<{ className?: string }>;
  title: string;
  description: string;
  time: string;
}

function ActivityItem({ icon: Icon, title, description, time }: ActivityItemProps) {
  return (
    <div className="flex items-start space-x-3 p-3 rounded-lg hover:bg-accent/50 transition-colors">
      <div className="p-1.5 rounded bg-primary/10 mt-0.5">
        <Icon className="h-3 w-3 text-primary" />
      </div>
      <div className="flex-1 min-w-0">
        <p className="font-medium text-sm">{title}</p>
        <p className="text-xs text-muted-foreground">{description}</p>
        <p className="text-xs text-muted-foreground mt-1">{time}</p>
      </div>
    </div>
  );
}