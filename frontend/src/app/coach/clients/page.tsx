"use client";

import { useAuth } from '@/context/AuthContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { PageHeader } from '@/components/ui/page-header';
import { AppLayout } from '@/components/layout/AppLayout';
import { ThreeIconNav } from '@/components/navigation/ThreeIconNav';
import { RippleIcon } from '@/components/icons/RippleIcon';
import { Users, MessageCircle, Calendar, BarChart3, Settings, Bell } from 'lucide-react';

export default function ClientsPage() {
  const { user } = useAuth();

  return (
    <AppLayout>
      <ThreeIconNav />
      <div className="container mx-auto px-4 py-8 md:pt-20 pb-20">
        <PageHeader
          icon={RippleIcon as any}
          title="Clients"
          subtitle="Manage your coaching relationships and client interactions"
        />

        <div className="w-full max-w-6xl mx-auto">
          {/* Main Content Grid */}
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3 mb-8">
            {/* Client Management */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-foreground">
                  <Users className="w-5 h-5 text-primary" />
                  Client Management
                </CardTitle>
                <CardDescription className="text-muted-foreground">
                  View and manage your active clients
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  Coming soon: Comprehensive client management tools, contact information, and relationship status tracking
                </p>
              </CardContent>
            </Card>

            {/* Session History */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-foreground">
                  <Calendar className="w-5 h-5 text-primary" />
                  Session History
                </CardTitle>
                <CardDescription className="text-muted-foreground">
                  Track coaching sessions and progress
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  Coming soon: Session scheduling, history tracking, and progress analytics
                </p>
              </CardContent>
            </Card>

            {/* Client Insights */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-foreground">
                  <BarChart3 className="w-5 h-5 text-primary" />
                  Client Insights
                </CardTitle>
                <CardDescription className="text-muted-foreground">
                  Understand your clients' progress
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  Coming soon: AI-powered client insights, progress reports, and goal tracking
                </p>
              </CardContent>
            </Card>

            {/* Communication */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-foreground">
                  <MessageCircle className="w-5 h-5 text-primary" />
                  Communication
                </CardTitle>
                <CardDescription className="text-muted-foreground">
                  Stay connected with your clients
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  Coming soon: Messaging system, check-ins, and communication history
                </p>
              </CardContent>
            </Card>

            {/* Notifications */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-foreground">
                  <Bell className="w-5 h-5 text-primary" />
                  Notifications
                </CardTitle>
                <CardDescription className="text-muted-foreground">
                  Stay updated on client activities
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  Coming soon: Real-time notifications, reminders, and activity alerts
                </p>
              </CardContent>
            </Card>

            {/* Client Settings */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-foreground">
                  <Settings className="w-5 h-5 text-primary" />
                  Client Settings
                </CardTitle>
                <CardDescription className="text-muted-foreground">
                  Configure client preferences
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  Coming soon: Client-specific settings, preferences, and customization options
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Welcome Message */}
          <div className="mt-12">
            <Card className="max-w-4xl mx-auto">
              <CardHeader>
                <CardTitle className="text-foreground">Welcome to Your Client Hub</CardTitle>
                <CardDescription className="text-muted-foreground">
                  Your central command center for managing client relationships
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground mb-4">
                  This client hub will be your comprehensive solution for managing all aspects of your coaching relationships.
                  From client onboarding and session management to progress tracking and communication, everything you need
                  to provide exceptional coaching experiences will be available here.
                </p>
                {user?.role === 'coach' && (
                  <div className="mt-4 p-4 bg-primary/10 border border-primary/20 rounded-lg">
                    <p className="text-sm text-primary">
                      <strong>Coach Client Hub:</strong> You're viewing the client management interface designed specifically for coaches.
                    </p>
                  </div>
                )}
                <div className="mt-6 text-sm text-muted-foreground">
                  <p className="font-medium mb-2">Features in development:</p>
                  <ul className="list-disc list-inside space-y-1">
                    <li>Client onboarding and profile management</li>
                    <li>Session scheduling and history tracking</li>
                    <li>Progress monitoring and goal tracking</li>
                    <li>Communication and messaging tools</li>
                    <li>Client insights and analytics</li>
                    <li>Automated reminders and notifications</li>
                  </ul>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}