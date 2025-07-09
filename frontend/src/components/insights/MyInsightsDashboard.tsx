'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  FileText, 
  Share2, 
  Calendar, 
  Tag, 
  Plus, 
  Loader2,
  Eye,
  MoreVertical,
  Users
} from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { sessionInsightService, SessionInsight } from '@/services/sessionInsightService';
import { InsightSharingModal } from './InsightSharingModal';
import { useAuth } from '@/context/AuthContext';

interface MyInsightsDashboardProps {
  onCreateNew?: () => void;
  onViewInsight?: (insight: SessionInsight) => void;
}

export function MyInsightsDashboard({ onCreateNew, onViewInsight }: MyInsightsDashboardProps) {
  const { getAuthToken } = useAuth();
  const [insights, setInsights] = useState<SessionInsight[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedInsightForSharing, setSelectedInsightForSharing] = useState<SessionInsight | null>(null);
  const [isShareModalOpen, setIsShareModalOpen] = useState(false);

  useEffect(() => {
    fetchInsights();
  }, []);

  const fetchInsights = async () => {
    try {
      setLoading(true);
      setError(null);
      const token = await getAuthToken();
      if (!token) {
        throw new Error("Authentication token not available");
      }
      const data = await sessionInsightService.getMyInsights(token);
      setInsights(data);
    } catch (err) {
      console.error('Error fetching insights:', err);
      setError('Failed to load insights. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleShareInsight = (insight: SessionInsight) => {
    setSelectedInsightForSharing(insight);
    setIsShareModalOpen(true);
  };

  const handleShareSuccess = () => {
    fetchInsights(); // Refresh insights to show updated sharing status
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const InsightCard = ({ insight, showSharedIndicator = false }: { 
    insight: SessionInsight; 
    showSharedIndicator?: boolean;
  }) => (
    <Card key={insight.id} className="hover:shadow-md transition-shadow">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle className="text-lg line-clamp-2">
              {insight.session_title || insight.title || 'Untitled Insight'}
            </CardTitle>
            <div className="flex items-center gap-2 mt-2 text-sm text-gray-600">
              <Calendar className="h-4 w-4" />
              <span>{formatDate(insight.created_at)}</span>
              {showSharedIndicator && (
                <>
                  <span>•</span>
                  <div className="flex items-center gap-1">
                    <Users className="h-4 w-4" />
                    <span>Shared with you</span>
                  </div>
                </>
              )}
            </div>
          </div>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="sm">
                <MoreVertical className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => onViewInsight?.(insight)}>
                <Eye className="mr-2 h-4 w-4" />
                View Details
              </DropdownMenuItem>
              {!showSharedIndicator && (
                <DropdownMenuItem onClick={() => handleShareInsight(insight)}>
                  <Share2 className="mr-2 h-4 w-4" />
                  Share with Coach
                </DropdownMenuItem>
              )}
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </CardHeader>
      <CardContent>
        <p className="text-gray-700 line-clamp-3 mb-4">
          {insight.session_summary || insight.content || 'No content available'}
        </p>
        
        {insight.key_themes && insight.key_themes.length > 0 && (
          <div className="flex flex-wrap gap-1 mb-3">
            {insight.key_themes.map((theme, index) => (
              <Badge key={index} variant="secondary" className="text-xs">
                <Tag className="mr-1 h-3 w-3" />
                {theme}
              </Badge>
            ))}
          </div>
        )}

        {insight.shared_with && insight.shared_with.length > 0 && (
          <div className="flex items-center gap-2 text-sm text-blue-600">
            <Share2 className="h-4 w-4" />
            <span>Shared with {insight.shared_with.length} coach{insight.shared_with.length > 1 ? 'es' : ''}</span>
          </div>
        )}
      </CardContent>
    </Card>
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading your insights...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <div className="text-red-600 mb-4">
          <FileText className="h-12 w-12 mx-auto mb-2 opacity-50" />
          <p className="font-medium">Error Loading Insights</p>
          <p className="text-sm">{error}</p>
        </div>
        <Button onClick={fetchInsights} variant="outline">
          Try Again
        </Button>
      </div>
    );
  }

  // For now, treat all insights as "my insights" since the backend endpoint returns user's insights
  // TODO: Implement proper separation of shared insights when backend supports it
  const myInsights = insights || [];
  const sharedWithMe: SessionInsight[] = []; // Empty for now
  const allInsights = [...myInsights, ...sharedWithMe];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">My Insights</h1>
          <p className="text-gray-600">Manage your personal insights and shared content</p>
        </div>
        <Button onClick={onCreateNew} className="flex items-center gap-2">
          <Plus className="h-4 w-4" />
          Create New Insight
        </Button>
      </div>

      <Tabs defaultValue="all" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="all">
            All ({allInsights.length})
          </TabsTrigger>
          <TabsTrigger value="my-insights">
            My Insights ({myInsights.length})
          </TabsTrigger>
          <TabsTrigger value="shared">
            Shared with Me ({sharedWithMe.length})
          </TabsTrigger>
        </TabsList>

        <TabsContent value="all" className="space-y-4">
          {allInsights.length === 0 ? (
            <div className="text-center py-12">
              <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No insights yet</h3>
              <p className="text-gray-600 mb-6">
                Create your first personal insight to get started
              </p>
              <Button onClick={onCreateNew}>
                <Plus className="mr-2 h-4 w-4" />
                Create Your First Insight
              </Button>
            </div>
          ) : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {myInsights.map((insight) => (
                <InsightCard key={insight.id} insight={insight} />
              ))}
              {sharedWithMe.map((insight) => (
                <InsightCard key={insight.id} insight={insight} showSharedIndicator />
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="my-insights" className="space-y-4">
          {myInsights.length === 0 ? (
            <div className="text-center py-12">
              <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No personal insights yet</h3>
              <p className="text-gray-600 mb-6">
                Create your first personal insight from your reflections or notes
              </p>
              <Button onClick={onCreateNew}>
                <Plus className="mr-2 h-4 w-4" />
                Create Personal Insight
              </Button>
            </div>
          ) : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {myInsights.map((insight) => (
                <InsightCard key={insight.id} insight={insight} />
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="shared" className="space-y-4">
          {sharedWithMe.length === 0 ? (
            <div className="text-center py-12">
              <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No shared insights</h3>
              <p className="text-gray-600">
                Insights shared with you by coaches will appear here
              </p>
            </div>
          ) : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {sharedWithMe.map((insight) => (
                <InsightCard key={insight.id} insight={insight} showSharedIndicator />
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>

      <InsightSharingModal
        insight={selectedInsightForSharing}
        isOpen={isShareModalOpen}
        onClose={() => {
          setIsShareModalOpen(false);
          setSelectedInsightForSharing(null);
        }}
        onSuccess={handleShareSuccess}
      />
    </div>
  );
}