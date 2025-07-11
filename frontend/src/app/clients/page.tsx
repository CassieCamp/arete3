"use client";

import { useAuth } from '@/context/AuthContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { RippleIcon } from '@/components/icons/RippleIcon';

export default function ClientsPage() {
  const { user } = useAuth();

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="flex justify-center mb-4">
              <RippleIcon className="w-16 h-16 text-primary" />
            </div>
            <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
              Clients
            </h1>
            <p className="text-lg text-gray-600 dark:text-gray-300">
              Manage your coaching relationships and client interactions
            </p>
          </div>

          {/* Main Content */}
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {/* Placeholder Cards */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <RippleIcon className="w-5 h-5" />
                  Client Management
                </CardTitle>
                <CardDescription>
                  View and manage your active clients
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Coming soon: Comprehensive client management tools
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <RippleIcon className="w-5 h-5" />
                  Session History
                </CardTitle>
                <CardDescription>
                  Track coaching sessions and progress
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Coming soon: Session tracking and analytics
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <RippleIcon className="w-5 h-5" />
                  Client Insights
                </CardTitle>
                <CardDescription>
                  Understand your clients' progress
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Coming soon: AI-powered client insights
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Welcome Message */}
          <div className="mt-12 text-center">
            <Card className="max-w-2xl mx-auto">
              <CardHeader>
                <CardTitle>Welcome to Your Client Hub</CardTitle>
                <CardDescription>
                  This is your central place for managing client relationships
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600 dark:text-gray-400">
                  We're building powerful tools to help you provide the best coaching experience. 
                  This page will soon include client management, session tracking, progress analytics, 
                  and communication tools.
                </p>
                {user?.role === 'coach' && (
                  <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                    <p className="text-sm text-blue-700 dark:text-blue-300">
                      <strong>Coach Mode:</strong> You're viewing the coach interface for client management.
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}