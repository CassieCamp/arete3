"use client";

import { useAuth } from '@/context/AuthContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { PageHeader } from '@/components/navigation/NavigationUtils';
import { Users, FileText, Target, Brain, Plus } from 'lucide-react';
import Link from 'next/link';

export default function DashboardPage() {
  const { user } = useAuth();

  const quickActions = [
    {
      title: 'Manage Connections',
      description: 'View and manage your coaching relationships',
      href: '/dashboard/connections',
      icon: Users,
      color: 'bg-blue-500'
    },
    {
      title: 'Upload Documents',
      description: 'Add new documents for analysis',
      href: '/dashboard/documents/upload',
      icon: FileText,
      color: 'bg-green-500'
    },
    {
      title: 'Set Goals',
      description: 'Create and track your goals',
      href: '/dashboard/goals',
      icon: Target,
      color: 'bg-purple-500'
    },
    {
      title: 'View Insights',
      description: 'Explore AI-powered session insights',
      href: '/dashboard/insights',
      icon: Brain,
      color: 'bg-orange-500'
    }
  ];

  return (
    <div>
      <PageHeader />
      
      <div className="space-y-6">
        {/* Welcome Section */}
        <Card>
          <CardHeader>
            <CardTitle>Welcome back, {user?.firstName}!</CardTitle>
            <CardDescription>
              {user?.role === 'coach' 
                ? 'Manage your clients and track their progress with AI-enhanced insights.'
                : 'Continue your growth journey with personalized coaching and insights.'
              }
            </CardDescription>
          </CardHeader>
        </Card>

        {/* Quick Actions */}
        <div>
          <h2 className="text-lg font-semibold mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {quickActions.map((action) => (
              <Link key={action.title} href={action.href}>
                <Card className="hover:shadow-md transition-shadow cursor-pointer">
                  <CardContent className="p-6">
                    <div className="flex items-center space-x-3">
                      <div className={`p-2 rounded-lg ${action.color}`}>
                        <action.icon className="h-5 w-5 text-white" />
                      </div>
                      <div>
                        <h3 className="font-medium">{action.title}</h3>
                        <p className="text-sm text-muted-foreground">{action.description}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        </div>

        {/* Recent Activity Placeholder */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
            <CardDescription>
              Your latest coaching activities and insights
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-center py-8 text-muted-foreground">
              <Brain className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>No recent activity to display</p>
              <p className="text-sm">Start by connecting with others or uploading documents</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}