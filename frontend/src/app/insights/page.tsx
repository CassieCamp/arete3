"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/context/AuthContext";
import { useRouter } from "next/navigation";
import { sessionInsightService, SessionInsight, SessionInsightListResponse } from "@/services/sessionInsightService";
import { InsightSubmissionComponent } from "@/components/insights/InsightSubmissionComponent";
import { InsightsTimelineComponent } from "@/components/insights/InsightsTimelineComponent";
import { InsightDetailView } from "@/components/insights/InsightDetailView";
import { MyInsightsDashboard } from "@/components/insights/MyInsightsDashboard";
import { UnpairedInsightUpload } from "@/components/insights/UnpairedInsightUpload";
import { PageHeader } from "@/components/navigation/NavigationUtils";

interface CoachingRelationship {
  id: string;
  coach_user_id: string;
  client_user_id: string;
  status: "pending" | "active" | "declined";
  created_at: string;
  updated_at: string;
  coach_email?: string;
  client_email?: string;
}

interface UserRelationships {
  pending: CoachingRelationship[];
  active: CoachingRelationship[];
}

export default function SessionInsightsPage() {
  const { user, isAuthenticated, getAuthToken } = useAuth();
  const router = useRouter();
  
  // State management
  const [relationships, setRelationships] = useState<UserRelationships>({
    pending: [],
    active: []
  });
  const [selectedRelationship, setSelectedRelationship] = useState<CoachingRelationship | null>(null);
  const [insights, setInsights] = useState<SessionInsightListResponse | null>(null);
  const [selectedInsight, setSelectedInsight] = useState<string | null>(null);
  const [currentView, setCurrentView] = useState<'my-insights' | 'selection' | 'timeline' | 'submission' | 'detail' | 'upload-unpaired'>('my-insights');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch relationships on component mount
  useEffect(() => {
    if (isAuthenticated && user) {
      fetchRelationships();
    }
  }, [isAuthenticated, user]);

  const fetchRelationships = async () => {
    try {
      setLoading(true);
      const token = await getAuthToken();
      if (!token) {
        throw new Error("No authentication token available");
      }

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/coaching-relationships/`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to fetch relationships");
      }

      const data: UserRelationships = await response.json();
      setRelationships(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch relationships");
    } finally {
      setLoading(false);
    }
  };

  const fetchInsightsForRelationship = async (relationshipId: string) => {
    try {
      setLoading(true);
      const token = await getAuthToken();
      if (!token) {
        throw new Error("No authentication token available");
      }

      const insightsData = await sessionInsightService.getSessionInsightsForRelationship(
        token,
        relationshipId
      );
      setInsights(insightsData);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch insights");
    } finally {
      setLoading(false);
    }
  };

  const handleRelationshipSelect = async (relationship: CoachingRelationship) => {
    setSelectedRelationship(relationship);
    setCurrentView('timeline');
    await fetchInsightsForRelationship(relationship.id);
  };

  const handleNewInsight = () => {
    setCurrentView('submission');
  };

  const handleInsightCreated = async () => {
    setCurrentView('timeline');
    if (selectedRelationship) {
      await fetchInsightsForRelationship(selectedRelationship.id);
    }
  };

  const handleInsightSelect = (insightId: string) => {
    setSelectedInsight(insightId);
    setCurrentView('detail');
  };

  const handleBackToTimeline = () => {
    setSelectedInsight(null);
    setCurrentView('timeline');
  };

  const handleBackToSelection = () => {
    setSelectedRelationship(null);
    setInsights(null);
    setCurrentView('selection');
  };

  const handleBackToMyInsights = () => {
    setSelectedRelationship(null);
    setInsights(null);
    setSelectedInsight(null);
    setCurrentView('my-insights');
  };

  const handleCreateUnpairedInsight = () => {
    setCurrentView('upload-unpaired');
  };

  const handleUnpairedInsightCreated = () => {
    setCurrentView('my-insights');
  };

  const handleViewInsight = (insight: SessionInsight) => {
    setSelectedInsight(insight.id);
    setCurrentView('detail');
  };

  const handleViewRelationshipInsights = () => {
    setCurrentView('selection');
  };

  const getOtherUserName = (relationship: CoachingRelationship) => {
    if (relationship.coach_user_id === user?.id) {
      return relationship.client_email || `Client ${relationship.client_user_id}`;
    } else {
      return relationship.coach_email || `Coach ${relationship.coach_user_id}`;
    }
  };

  const getRelationshipRole = (relationship: CoachingRelationship) => {
    return relationship.coach_user_id === user?.id ? "Coach" : "Client";
  };

  // Show loading while authentication is being determined
  if (isAuthenticated === undefined) {
    return (
      <div>
        <PageHeader />
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // Show loading while user data is being loaded
  if (isAuthenticated && !user) {
    return (
      <div>
        <PageHeader />
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading user data...</p>
        </div>
      </div>
    );
  }

  // If not authenticated, redirect
  if (!isAuthenticated) {
    return (
      <div>
        <PageHeader />
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto mb-4"></div>
          <p className="text-gray-600">Redirecting...</p>
        </div>
      </div>
    );
  }

  return (
    <div>
      <PageHeader />
      <div className="space-y-6">

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 text-red-800 border border-red-200 rounded-md">
            <p className="font-medium">Error</p>
            <p className="text-sm">{error}</p>
            <Button
              onClick={() => {
                setError(null);
                if (currentView === 'selection') {
                  fetchRelationships();
                } else if (selectedRelationship) {
                  fetchInsightsForRelationship(selectedRelationship.id);
                }
              }}
              variant="outline"
              size="sm"
              className="mt-2"
            >
              Try Again
            </Button>
          </div>
        )}

        {/* My Insights Dashboard View */}
        {currentView === 'my-insights' && (
          <div className="space-y-6">
            {/* Navigation Header */}
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold">Insights</h1>
                <p className="text-gray-600">Manage your personal insights and coaching relationships</p>
              </div>
              <Button
                onClick={handleViewRelationshipInsights}
                variant="outline"
                className="flex items-center gap-2"
              >
                View Relationship Insights
              </Button>
            </div>
            
            <MyInsightsDashboard
              onCreateNew={handleCreateUnpairedInsight}
              onViewInsight={handleViewInsight}
            />
          </div>
        )}

        {/* Unpaired Insight Upload View */}
        {currentView === 'upload-unpaired' && (
          <div className="space-y-6">
            {/* Navigation */}
            <div className="flex items-center gap-4">
              <Button
                onClick={handleBackToMyInsights}
                variant="outline"
                size="sm"
              >
                ← Back to My Insights
              </Button>
            </div>
            
            <UnpairedInsightUpload
              onSuccess={handleUnpairedInsightCreated}
              onCancel={handleBackToMyInsights}
            />
          </div>
        )}

        {/* Relationship Selection View */}
        {currentView === 'selection' && (
          <div className="space-y-6">
            {/* Navigation */}
            <div className="flex items-center gap-4">
              <Button
                onClick={handleBackToMyInsights}
                variant="outline"
                size="sm"
              >
                ← Back to My Insights
              </Button>
            </div>
            
            <Card>
              <CardHeader>
                <CardTitle>Select a Coaching Relationship</CardTitle>
                <CardDescription>
                  Choose a coaching relationship to view or create session insights
                </CardDescription>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <div className="text-center py-8">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
                    <p className="text-gray-600">Loading relationships...</p>
                  </div>
                ) : relationships.active.length === 0 ? (
                  <div className="text-center py-8">
                    <div className="text-4xl mb-4">🤝</div>
                    <h3 className="text-lg font-medium text-gray-900 mb-2">
                      No active coaching relationships
                    </h3>
                    <p className="text-gray-600 mb-6">
                      You need an active coaching relationship to create session insights.
                    </p>
                    <Button
                      onClick={() => router.push('/connections')}
                      className="bg-blue-600 hover:bg-blue-700"
                    >
                      Manage Connections
                    </Button>
                  </div>
                ) : (
                  <div className="grid gap-4">
                    {relationships.active.map((relationship) => (
                      <div
                        key={relationship.id}
                        className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
                        onClick={() => handleRelationshipSelect(relationship)}
                      >
                        <div className="flex justify-between items-center">
                          <div>
                            <p className="font-medium text-gray-900">
                              {getOtherUserName(relationship)}
                            </p>
                            <p className="text-sm text-gray-600">
                              Your role: {getRelationshipRole(relationship)}
                            </p>
                            <p className="text-xs text-gray-500">
                              Connected: {new Date(relationship.updated_at).toLocaleDateString()}
                            </p>
                          </div>
                          <div className="flex items-center space-x-2">
                            <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                              Active
                            </span>
                            <span className="text-gray-400">→</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        )}

        {/* Timeline View */}
        {currentView === 'timeline' && selectedRelationship && (
          <InsightsTimelineComponent
            relationship={selectedRelationship}
            insights={insights}
            loading={loading}
            onNewInsight={handleNewInsight}
            onInsightSelect={handleInsightSelect}
            onBack={handleBackToSelection}
            getOtherUserName={getOtherUserName}
          />
        )}

        {/* Submission View */}
        {currentView === 'submission' && selectedRelationship && (
          <InsightSubmissionComponent
            relationship={selectedRelationship}
            onInsightCreated={handleInsightCreated}
            onBack={handleBackToTimeline}
            getOtherUserName={getOtherUserName}
          />
        )}

        {/* Detail View */}
        {currentView === 'detail' && selectedInsight && (
          <div className="space-y-6">
            {/* Navigation */}
            <div className="flex items-center gap-4">
              <Button
                onClick={selectedRelationship ? handleBackToTimeline : handleBackToMyInsights}
                variant="outline"
                size="sm"
              >
                ← Back to {selectedRelationship ? 'Timeline' : 'My Insights'}
              </Button>
            </div>
            
            <InsightDetailView
              insightId={selectedInsight}
              onBack={selectedRelationship ? handleBackToTimeline : handleBackToMyInsights}
            />
          </div>
        )}
      </div>
    </div>
  );
}