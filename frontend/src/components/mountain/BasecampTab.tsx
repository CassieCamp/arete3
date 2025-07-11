'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { formatDistanceToNow } from 'date-fns';
import { DocumentList, DocumentUpload } from '@/components/dashboard/documents';
import { useEntryService, Entry } from '@/services/entryService';

interface Destination {
  id: string;
  goal_statement: string;
  success_vision: string;
  is_big_idea: boolean;
  big_idea_rank?: number;
  progress_percentage?: number;
  progress_emoji: string;
  progress_notes?: string;
  priority: string;
  category: string;
  status: string;
  tags: string[];
  created_at: string;
  updated_at: string;
}

export function BasecampTab() {
  const { getAuthToken } = useAuth();
  const entryService = useEntryService();
  const [entries, setEntries] = useState<Entry[]>([]);
  const [destinations, setDestinations] = useState<Destination[]>([]);
  const [loading, setLoading] = useState(true);
  const [destinationsLoading, setDestinationsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [destinationsError, setDestinationsError] = useState<string | null>(null);
  const [showUpload, setShowUpload] = useState(false);

  useEffect(() => {
    fetchRecentEntries();
    fetchDestinations();
  }, []);

  const fetchRecentEntries = async () => {
    try {
      const data = await entryService.getEntries({ limit: 3 });
      setEntries(data.entries || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const fetchDestinations = async () => {
    try {
      const token = await getAuthToken();
      const response = await fetch('/api/v1/goals', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch destinations');
      }

      const data = await response.json();
      setDestinations(data || []);
    } catch (err) {
      setDestinationsError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setDestinationsLoading(false);
    }
  };

  const handleUploadSuccess = () => {
    setShowUpload(false);
    // Refresh documents will happen automatically via DocumentList component
  };

  const handleUploadClick = () => {
    setShowUpload(true);
  };

  const getTypeLabel = (type: string) => {
    return type === 'fresh_thought' ? 'Fresh Thought' : 'Session';
  };

  const getTypeColor = (type: string) => {
    return type === 'fresh_thought' ? 'bg-green-100 text-green-800' : 'bg-blue-100 text-blue-800';
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'bg-red-100 text-red-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'low':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  // Get top 3 big ideas for the card
  const topBigIdeas = destinations
    .filter(d => d.is_big_idea)
    .sort((a, b) => (a.big_idea_rank || 0) - (b.big_idea_rank || 0))
    .slice(0, 3);

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto"></div>
          <p className="mt-2 text-gray-600">Loading your recent activity...</p>
        </div>
      </div>
    );
  }



  return (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <div className="text-4xl mb-2">🏕️</div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Welcome to Basecamp</h2>
        <p className="text-gray-600">Your most recent activity and progress</p>
      </div>

      {/* Overview Section */}
      <div className="space-y-6">
        {error ? (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">⚠️</div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Error Loading Entries</h3>
            <p className="text-red-600 mb-6">
              {error}
            </p>
            <p className="text-gray-600">
              The Documents section is still available below.
            </p>
          </div>
        ) : entries.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">📝</div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">No Recent Activity</h3>
            <p className="text-gray-600 mb-6">
              Your recent entries and activity will appear here. Start by creating your first entry!
            </p>
          </div>
        ) : (
          <div className="grid gap-6">
            {entries.map((entry) => (
              <Card key={entry.id} className="hover:shadow-md transition-shadow">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">{entry.title}</CardTitle>
                    <div className="flex items-center gap-2">
                      <Badge className={getTypeColor(entry.entry_type)}>
                        {getTypeLabel(entry.entry_type)}
                      </Badge>
                      <span className="text-sm text-gray-500">
                        {formatDistanceToNow(new Date(entry.created_at), { addSuffix: true })}
                      </span>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  {entry.content && (
                    <p className="text-gray-700 mb-4 line-clamp-3">{entry.content}</p>
                  )}
                  
                  {entry.has_insights && (
                    <div className="mt-4">
                      <Badge variant="outline" className="text-xs">
                        ✨ Has Insights
                      </Badge>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* Documents Card */}
      <Card className="mt-8">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            📄 Documents
          </CardTitle>
        </CardHeader>
        <CardContent>
          {showUpload ? (
            <DocumentUpload
              onUploadSuccess={handleUploadSuccess}
              onCancel={() => setShowUpload(false)}
              compact={true}
            />
          ) : (
            <DocumentList
              limit={6}
              showUploadButton={true}
              onUploadClick={handleUploadClick}
              compact={true}
            />
          )}
        </CardContent>
      </Card>

      {/* Destinations Card */}
      <Card className="mt-8">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            🎯 Destinations
          </CardTitle>
        </CardHeader>
        <CardContent>
          {destinationsLoading ? (
            <div className="text-center py-4">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-gray-900 mx-auto"></div>
              <p className="mt-2 text-sm text-gray-600">Loading destinations...</p>
            </div>
          ) : destinationsError ? (
            <div className="text-center py-4">
              <p className="text-sm text-red-600">Error loading destinations: {destinationsError}</p>
            </div>
          ) : topBigIdeas.length === 0 ? (
            <div className="text-center py-6">
              <div className="text-3xl mb-2">💡</div>
              <h4 className="text-sm font-medium text-gray-600 mb-1">No Big Ideas Yet</h4>
              <p className="text-xs text-gray-500">
                Your three most important goals will appear here when you create them.
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {topBigIdeas.map((idea, index) => (
                <div key={idea.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <Badge variant="outline" className="text-xs">
                        #{idea.big_idea_rank || index + 1}
                      </Badge>
                      <span className="text-lg">{idea.progress_emoji}</span>
                    </div>
                    <h5 className="font-medium text-sm text-gray-900 mb-1">{idea.goal_statement}</h5>
                    <p className="text-xs text-gray-600 line-clamp-2">{idea.success_vision}</p>
                  </div>
                  <div className="ml-3 text-right">
                    <Badge className={getPriorityColor(idea.priority)} variant="outline">
                      {idea.priority}
                    </Badge>
                    {idea.progress_percentage !== null && (
                      <div className="mt-1 text-xs text-gray-500">
                        {idea.progress_percentage}%
                      </div>
                    )}
                  </div>
                </div>
              ))}
              {destinations.filter(d => !d.is_big_idea).length > 0 && (
                <div className="pt-2 border-t border-gray-200">
                  <p className="text-xs text-gray-500 text-center">
                    +{destinations.filter(d => !d.is_big_idea).length} other destinations
                  </p>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}