'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/context/AuthContext';
import apiClient from '@/lib/apiClient';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { PageHeader } from '@/components/ui/page-header';
import { AppLayout } from '@/components/layout/AppLayout';
import { ThreeIconNav } from '@/components/navigation/ThreeIconNav';
import { Users, Clock, FileText, Plus, Eye, MessageSquare, BookOpen, Settings } from 'lucide-react';
import { ClientManagement } from '@/components/coach/ClientManagement';
import { ResourceManagement } from '@/components/coach/ResourceManagement';
import { TemplateManagement } from '@/components/coach/TemplateManagement';

interface CoachClient {
  id: string;
  name: string;
  email: string;
  relationship_status: string;
  entries_count: number;
  last_entry_date: string | null;
  created_at: string;
}

interface CoachResource {
  id: string;
  title: string;
  description: string;
  resource_url: string;
  resource_type: string;
  is_template: boolean;
  client_specific: boolean;
  target_client_id: string | null;
  category: string;
  tags: string[];
  created_at: string;
}

interface CoachDashboardData {
  clients: CoachClient[];
  total_clients: number;
  active_clients: number;
  pending_clients: number;
}

export default function CoachDashboard() {
  const { user, isAuthenticated, getAuthToken, currentOrganization, organizationRoles } = useAuth();
  const [dashboardData, setDashboardData] = useState<CoachDashboardData | null>(null);
  const [resources, setResources] = useState<CoachResource[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'clients' | 'resources' | 'templates'>('clients');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    console.log("CoachDashboard: isAuthenticated:", isAuthenticated, "user:", !!user, "organizationRoles:", organizationRoles);
    if (isAuthenticated && user) {
      loadCoachData();
    }
  }, [isAuthenticated, user, organizationRoles]);

  const loadCoachData = async () => {
    try {
      setIsLoading(true);
      setError(null);

      const token = await getAuthToken();
      if (!token) {
        throw new Error('No authentication token available');
      }

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const orgId = currentOrganization || undefined;
      
      console.log("CoachDashboard: Loading data with orgId:", orgId);

      const [clientsData, resourcesData] = await Promise.all([
        apiClient.get("/coach/clients", token, orgId),
        apiClient.get("/coach/resources", token, orgId),
      ]);

      setDashboardData(clientsData);
      setResources(resourcesData.resources || []);
    } catch (error) {
      console.error('Failed to load coach data:', error);
      setError(error instanceof Error ? error.message : 'Failed to load coach data');
    } finally {
      setIsLoading(false);
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Card className="w-96">
          <CardHeader>
            <CardTitle>Access Denied</CardTitle>
            <CardDescription>Please sign in to access the coach dashboard.</CardDescription>
          </CardHeader>
        </Card>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Card className="w-96">
          <CardHeader>
            <CardTitle className="text-red-600">Error</CardTitle>
            <CardDescription>{error}</CardDescription>
          </CardHeader>
          <CardContent>
            <Button onClick={loadCoachData} className="w-full">
              Try Again
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="max-w-6xl mx-auto p-6">
        <div className="mb-8">
          <div className="h-8 bg-gray-200 rounded w-64 mb-2 animate-pulse"></div>
          <div className="h-4 bg-gray-200 rounded w-96 animate-pulse"></div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="bg-white rounded-lg border border-gray-200 p-6">
              <div className="animate-pulse">
                <div className="h-12 w-12 bg-gray-200 rounded-lg mb-4"></div>
                <div className="h-4 bg-gray-200 rounded w-24 mb-2"></div>
                <div className="h-8 bg-gray-200 rounded w-16"></div>
              </div>
            </div>
          ))}
        </div>
        
        <div className="h-96 bg-gray-200 rounded animate-pulse"></div>
      </div>
    );
  }

  const templates = resources.filter(r => r.is_template);
  const regularResources = resources.filter(r => !r.is_template);

  return (
    <AppLayout>
      <ThreeIconNav />
      <div className="container mx-auto px-4 py-8 md:pt-20 pb-20">
        <PageHeader
          icon={Settings}
          title="Coach Dashboard"
          subtitle="Manage your clients, resources, and coaching materials"
        />

        <div className="w-full max-w-6xl mx-auto">
          {/* Quick Stats */}
          {dashboardData && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center">
                    <div className="p-2 bg-blue-100 rounded-lg">
                      <Users className="w-6 h-6 text-blue-600" />
                    </div>
                    <div className="ml-4">
                      <p className="text-sm font-medium text-gray-600">Active Clients</p>
                      <p className="text-2xl font-semibold text-gray-900">{dashboardData.active_clients}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center">
                    <div className="p-2 bg-orange-100 rounded-lg">
                      <Clock className="w-6 h-6 text-orange-600" />
                    </div>
                    <div className="ml-4">
                      <p className="text-sm font-medium text-gray-600">Pending Invites</p>
                      <p className="text-2xl font-semibold text-gray-900">{dashboardData.pending_clients}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center">
                    <div className="p-2 bg-green-100 rounded-lg">
                      <FileText className="w-6 h-6 text-green-600" />
                    </div>
                    <div className="ml-4">
                      <p className="text-sm font-medium text-gray-600">Total Entries</p>
                      <p className="text-2xl font-semibold text-gray-900">
                        {dashboardData.clients.reduce((sum, client) => sum + client.entries_count, 0)}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Main Content Tabs */}
          <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as any)} className="space-y-6">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="clients" className="flex items-center gap-2">
                <Users className="w-4 h-4" />
                Clients
                <Badge variant="secondary" className="ml-1">
                  {dashboardData?.total_clients || 0}
                </Badge>
              </TabsTrigger>
              <TabsTrigger value="resources" className="flex items-center gap-2">
                <BookOpen className="w-4 h-4" />
                Resources
                <Badge variant="secondary" className="ml-1">
                  {regularResources.length}
                </Badge>
              </TabsTrigger>
              <TabsTrigger value="templates" className="flex items-center gap-2">
                <FileText className="w-4 h-4" />
                Templates
                <Badge variant="secondary" className="ml-1">
                  {templates.length}
                </Badge>
              </TabsTrigger>
            </TabsList>

            <TabsContent value="clients" className="space-y-6">
              {dashboardData && (
                <ClientManagement
                  clients={dashboardData.clients}
                  onUpdate={loadCoachData}
                />
              )}
            </TabsContent>

            <TabsContent value="resources" className="space-y-6">
              <ResourceManagement
                resources={regularResources}
                onUpdate={loadCoachData}
              />
            </TabsContent>

            <TabsContent value="templates" className="space-y-6">
              <TemplateManagement
                templates={templates}
                onUpdate={loadCoachData}
              />
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </AppLayout>
  );
}