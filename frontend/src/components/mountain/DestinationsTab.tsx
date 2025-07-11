'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { formatDistanceToNow } from 'date-fns';

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

export function DestinationsTab() {
  const { getAuthToken } = useAuth();
  const [destinations, setDestinations] = useState<Destination[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDestinations();
  }, []);

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
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
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

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'professional':
        return 'bg-blue-100 text-blue-800';
      case 'personal':
        return 'bg-purple-100 text-purple-800';
      case 'health':
        return 'bg-green-100 text-green-800';
      case 'relationships':
        return 'bg-pink-100 text-pink-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  // Separate big ideas from regular destinations
  const bigIdeas = destinations
    .filter(d => d.is_big_idea)
    .sort((a, b) => (a.big_idea_rank || 0) - (b.big_idea_rank || 0));
  
  const regularDestinations = destinations.filter(d => !d.is_big_idea);

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto"></div>
          <p className="mt-2 text-gray-600">Loading your destinations...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <p className="text-red-600">Error loading destinations: {error}</p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="text-center mb-8">
        <div className="text-4xl mb-2">🎯</div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Your Destinations</h2>
        <p className="text-gray-600">Focus on your three big ideas and track your progress toward your goals</p>
      </div>

      {/* Three Big Ideas Section */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-xl font-semibold text-gray-800">Three Big Ideas</h3>
            <p className="text-sm text-gray-600">
              Your most important destinations - the big picture goals that drive you.
            </p>
          </div>
        </div>
        
        {bigIdeas.length === 0 ? (
          <div className="text-center py-8">
            <div className="text-4xl mb-4">💡</div>
            <h4 className="text-lg font-medium text-gray-600 mb-2">No Big Ideas Yet</h4>
            <p className="text-gray-500">
              Your three most important goals will appear here when you create them.
            </p>
          </div>
        ) : (
          <div className="grid gap-6 md:grid-cols-3">
            {bigIdeas.map((idea, index) => (
              <Card key={idea.id} className="hover:shadow-md transition-shadow">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <Badge variant="outline" className="text-xs">
                      Big Idea #{idea.big_idea_rank || index + 1}
                    </Badge>
                    <span className="text-2xl">{idea.progress_emoji}</span>
                  </div>
                  <CardTitle className="text-lg">{idea.goal_statement}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-600 text-sm mb-4 line-clamp-3">
                    {idea.success_vision}
                  </p>
                  
                  <div className="flex items-center justify-between mb-3">
                    <Badge className={getPriorityColor(idea.priority)} variant="outline">
                      {idea.priority}
                    </Badge>
                    <Badge className={getCategoryColor(idea.category)} variant="outline">
                      {idea.category}
                    </Badge>
                  </div>
                  
                  {idea.progress_percentage !== null && (
                    <div className="mb-3">
                      <div className="flex items-center justify-between text-sm mb-1">
                        <span className="text-gray-600">Progress</span>
                        <span className="text-gray-900">{idea.progress_percentage}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${idea.progress_percentage}%` }}
                        ></div>
                      </div>
                    </div>
                  )}
                  
                  {idea.progress_notes && (
                    <p className="text-xs text-gray-500 mt-2">
                      {idea.progress_notes}
                    </p>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* Regular Destinations Section */}
      {regularDestinations.length > 0 && (
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <div className="mb-6">
            <h3 className="text-xl font-semibold text-gray-800">Other Destinations</h3>
            <p className="text-sm text-gray-600">
              Additional goals and aspirations you're working toward.
            </p>
          </div>
          
          <div className="grid gap-4 md:grid-cols-2">
            {regularDestinations.map((destination) => (
              <Card key={destination.id} className="hover:shadow-md transition-shadow">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">{destination.goal_statement}</CardTitle>
                    <span className="text-xl">{destination.progress_emoji}</span>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-600 text-sm mb-4 line-clamp-2">
                    {destination.success_vision}
                  </p>
                  
                  <div className="flex items-center gap-2 mb-3">
                    <Badge className={getPriorityColor(destination.priority)} variant="outline">
                      {destination.priority}
                    </Badge>
                    <Badge className={getCategoryColor(destination.category)} variant="outline">
                      {destination.category}
                    </Badge>
                    <Badge variant="outline" className="text-xs">
                      {destination.status}
                    </Badge>
                  </div>
                  
                  {destination.progress_percentage !== null && (
                    <div className="mb-3">
                      <div className="flex items-center justify-between text-sm mb-1">
                        <span className="text-gray-600">Progress</span>
                        <span className="text-gray-900">{destination.progress_percentage}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${destination.progress_percentage}%` }}
                        ></div>
                      </div>
                    </div>
                  )}
                  
                  {destination.tags.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-2">
                      {destination.tags.slice(0, 3).map((tag, index) => (
                        <Badge key={index} variant="outline" className="text-xs">
                          {tag}
                        </Badge>
                      ))}
                      {destination.tags.length > 3 && (
                        <Badge variant="outline" className="text-xs">
                          +{destination.tags.length - 3}
                        </Badge>
                      )}
                    </div>
                  )}
                  
                  <p className="text-xs text-gray-500 mt-2">
                    Updated {formatDistanceToNow(new Date(destination.updated_at), { addSuffix: true })}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Empty State for All Destinations */}
      {destinations.length === 0 && (
        <div className="text-center py-12">
          <div className="text-6xl mb-4">🎯</div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">No Destinations Yet</h3>
          <p className="text-gray-600 mb-6">
            Start by creating your first destination to track your goals and aspirations.
          </p>
        </div>
      )}
    </div>
  );
}