"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { SessionInsight, SessionInsightListResponse } from "@/services/sessionInsightService";

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

interface InsightsTimelineComponentProps {
  relationship: CoachingRelationship;
  insights: SessionInsightListResponse | null;
  loading: boolean;
  onNewInsight: () => void;
  onInsightSelect: (insightId: string) => void;
  onBack: () => void;
  getOtherUserName: (relationship: CoachingRelationship) => string;
}

export function InsightsTimelineComponent({
  relationship,
  insights,
  loading,
  onNewInsight,
  onInsightSelect,
  onBack,
  getOtherUserName
}: InsightsTimelineComponentProps) {

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'processing':
        return 'bg-yellow-100 text-yellow-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return '✅';
      case 'processing':
        return '⏳';
      case 'failed':
        return '❌';
      default:
        return '⏸️';
    }
  };

  const getQualityColor = (quality: string) => {
    switch (quality.toLowerCase()) {
      case 'excellent':
        return 'text-green-600';
      case 'good':
        return 'text-blue-600';
      case 'average':
        return 'text-yellow-600';
      case 'needs improvement':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-2xl font-bold text-gray-900">Session Insights</h3>
          <p className="text-sm text-gray-600">
            Coaching relationship with {getOtherUserName(relationship)}
          </p>
          {insights && (
            <p className="text-xs text-gray-500">
              {insights.total_count} insight{insights.total_count !== 1 ? 's' : ''} total
            </p>
          )}
        </div>
        <div className="flex space-x-3">
          <Button variant="outline" onClick={onBack}>
            ← Back to Relationships
          </Button>
          <Button onClick={onNewInsight} className="bg-blue-600 hover:bg-blue-700">
            + New Session Insight
          </Button>
        </div>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading session insights...</p>
        </div>
      )}

      {/* Empty State */}
      {!loading && insights && insights.insights.length === 0 && (
        <Card>
          <CardContent className="text-center py-12">
            <div className="text-6xl mb-4">🧠</div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              No session insights yet
            </h3>
            <p className="text-gray-600 mb-6">
              Create your first session insight by uploading a transcript or pasting session text.
            </p>
            <Button
              onClick={onNewInsight}
              className="bg-blue-600 hover:bg-blue-700"
            >
              Create Your First Insight
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Insights Timeline */}
      {!loading && insights && insights.insights.length > 0 && (
        <div className="space-y-4">
          {insights.insights.map((insight, index) => (
            <div style={{backgroundColor: 'oklch(0.9583 0.0111 89.7230)'}}>
            <Card
              key={insight.id}
              className="hover:shadow-lg transition-shadow cursor-pointer"
              onClick={() => onInsightSelect(insight.id)}
            >
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-1">
                      <CardTitle className="text-lg">
                        {insight.session_title || `Session Insight #${insights.insights.length - index}`}
                      </CardTitle>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(insight.status)}`}>
                        {getStatusIcon(insight.status)} {insight.status}
                      </span>
                    </div>
                    <CardDescription className="text-sm">
                      {insight.session_date 
                        ? `Session Date: ${new Date(insight.session_date).toLocaleDateString()}`
                        : `Created: ${formatDate(insight.created_at)}`
                      }
                    </CardDescription>
                  </div>
                  <div className="text-right">
                    <div className={`text-sm font-medium ${getQualityColor(insight.overall_session_quality)}`}>
                      {insight.overall_session_quality}
                    </div>
                    <div className="text-xs text-gray-500">
                      Session Quality
                    </div>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="pt-0">
                {/* Session Summary */}
                <div className="mb-4">
                  <p className="text-sm text-gray-700">
                    {insight.session_summary}
                  </p>
                </div>

                {/* Key Themes */}
                {insight.key_themes.length > 0 && (
                  <div className="mb-4">
                    <h5 className="text-xs font-medium text-gray-700 mb-2">Key Themes:</h5>
                    <div className="flex flex-wrap gap-1">
                      {insight.key_themes.slice(0, 3).map((theme, themeIndex) => (
                        <span 
                          key={themeIndex}
                          className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full"
                        >
                          {theme}
                        </span>
                      ))}
                      {insight.key_themes.length > 3 && (
                        <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
                          +{insight.key_themes.length - 3} more
                        </span>
                      )}
                    </div>
                  </div>
                )}

                {/* Insight Counts */}
                <div className="flex items-center justify-between text-xs text-gray-600">
                  <div className="flex space-x-4">
                    {insight.celebration_count > 0 && (
                      <span className="flex items-center space-x-1">
                        <span>🎉</span>
                        <span>{insight.celebration_count} celebration{insight.celebration_count !== 1 ? 's' : ''}</span>
                      </span>
                    )}
                    {insight.intention_count > 0 && (
                      <span className="flex items-center space-x-1">
                        <span>🎯</span>
                        <span>{insight.intention_count} intention{insight.intention_count !== 1 ? 's' : ''}</span>
                      </span>
                    )}
                    {insight.discovery_count > 0 && (
                      <span className="flex items-center space-x-1">
                        <span>💡</span>
                        <span>{insight.discovery_count} discover{insight.discovery_count !== 1 ? 'ies' : 'y'}</span>
                      </span>
                    )}
                    {insight.action_item_count > 0 && (
                      <span className="flex items-center space-x-1">
                        <span>✅</span>
                        <span>{insight.action_item_count} action{insight.action_item_count !== 1 ? 's' : ''}</span>
                      </span>
                    )}
                  </div>
                  <span className="text-gray-400">→ View Details</span>
                </div>
              </CardContent>
            </Card>
            </div>
          ))}
        </div>
      )}

      {/* Load More Button (if needed for pagination) */}
      {!loading && insights && insights.insights.length < insights.total_count && (
        <div className="text-center">
          <Button variant="outline">
            Load More Insights
          </Button>
        </div>
      )}
    </div>
  );
}