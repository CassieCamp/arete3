"use client";

import { useAuth } from '@/context/AuthContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Calendar, CreditCard, BarChart3, Settings, Users, FileText } from 'lucide-react';

export default function ConsolePage() {
  const { user } = useAuth();

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="flex justify-center mb-4">
              <BarChart3 className="w-16 h-16 text-primary" />
            </div>
            <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
              Console
            </h1>
            <p className="text-lg text-gray-600 dark:text-gray-300">
              Your business management hub for scheduling, billing, and analytics
            </p>
          </div>

          {/* Main Content Grid */}
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {/* Scheduling */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Calendar className="w-5 h-5" />
                  Scheduling
                </CardTitle>
                <CardDescription>
                  Manage appointments and availability
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Coming soon: Advanced scheduling tools, calendar integration, and automated booking
                </p>
              </CardContent>
            </Card>

            {/* Billing & Payments */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <CreditCard className="w-5 h-5" />
                  Billing & Payments
                </CardTitle>
                <CardDescription>
                  Handle invoices and payment processing
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Coming soon: Invoice generation, payment tracking, and financial reporting
                </p>
              </CardContent>
            </Card>

            {/* Analytics */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="w-5 h-5" />
                  Business Analytics
                </CardTitle>
                <CardDescription>
                  Track performance and growth metrics
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Coming soon: Revenue analytics, client retention metrics, and growth insights
                </p>
              </CardContent>
            </Card>

            {/* Client Management */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Users className="w-5 h-5" />
                  Client Database
                </CardTitle>
                <CardDescription>
                  Comprehensive client information system
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Coming soon: Client profiles, contact management, and communication history
                </p>
              </CardContent>
            </Card>

            {/* Documents & Contracts */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileText className="w-5 h-5" />
                  Documents
                </CardTitle>
                <CardDescription>
                  Contracts, agreements, and paperwork
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Coming soon: Contract templates, digital signatures, and document storage
                </p>
              </CardContent>
            </Card>

            {/* Settings */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Settings className="w-5 h-5" />
                  Business Settings
                </CardTitle>
                <CardDescription>
                  Configure your coaching business
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Coming soon: Business profile, pricing configuration, and service offerings
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Welcome Message */}
          <div className="mt-12 text-center">
            <Card className="max-w-3xl mx-auto">
              <CardHeader>
                <CardTitle>Welcome to Your Business Console</CardTitle>
                <CardDescription>
                  Your central command center for managing your coaching business
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600 dark:text-gray-400 mb-4">
                  This console will be your one-stop solution for all business operations. From scheduling 
                  and billing to analytics and client management, everything you need to run a successful 
                  coaching practice will be available here.
                </p>
                {user?.role === 'coach' && (
                  <div className="mt-4 p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                    <p className="text-sm text-green-700 dark:text-green-300">
                      <strong>Coach Console:</strong> You're viewing the business management interface designed specifically for coaches.
                    </p>
                  </div>
                )}
                <div className="mt-6 text-sm text-gray-500 dark:text-gray-400">
                  <p>Features in development:</p>
                  <ul className="list-disc list-inside mt-2 space-y-1">
                    <li>Automated scheduling with calendar sync</li>
                    <li>Integrated payment processing</li>
                    <li>Client progress tracking</li>
                    <li>Revenue and performance analytics</li>
                    <li>Document management system</li>
                    <li>Business reporting tools</li>
                  </ul>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}