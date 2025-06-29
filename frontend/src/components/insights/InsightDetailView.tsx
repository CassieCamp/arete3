"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/context/AuthContext";
import { sessionInsightService, SessionInsightDetail } from "@/services/sessionInsightService";

interface InsightDetailViewProps {
  insightId: string;
  onBack: () => void;
}

export function InsightDetailView({ insightId, onBack }: InsightDetailViewProps) {
  const { getAuthToken } = useAuth();
  const [insight, setInsight] = useState<SessionInsightDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchInsightDetail();
  }, [insightId]);

  const fetchInsightDetail = async () => {
    try {
      setLoading(true);
      setError(null);
      const token = await getAuthToken();
      if (!token) {
        throw new Error('Authentication token not available');
      }

      const insightData = await sessionInsightService.getSessionInsightDetail(token, insightId);
      setInsight(insightData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch insight details');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getCommitmentColor = (level: string) => {
    switch (level.toLowerCase()) {
      case 'high':
      case 'strong':
        return 'bg-green-100 text-green-800';
      case 'medium':
      case 'moderate':
        return 'bg-yellow-100 text-yellow-800';
      case 'low':
      case 'exploratory':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getProgressColor = (level: string) => {
    switch (level.toLowerCase()) {
      case 'significant':
        return 'bg-green-100 text-green-800';
      case 'moderate':
        return 'bg-blue-100 text-blue-800';
      case 'minimal':
        return 'bg-yellow-100 text-yellow-800';
      case 'setback':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getDepthColor = (level: string) => {
    switch (level.toLowerCase()) {
      case 'deep':
        return 'bg-purple-100 text-purple-800';
      case 'moderate':
        return 'bg-blue-100 text-blue-800';
      case 'surface':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getBreakthroughColor = (level: string) => {
    switch (level.toLowerCase()) {
      case 'major':
        return 'bg-green-100 text-green-800';
      case 'moderate':
        return 'bg-blue-100 text-blue-800';
      case 'minor':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-gray-600">Loading insight details...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <div className="text-red-600 mb-4">❌</div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">Error Loading Insight</h3>
        <p className="text-gray-600 mb-6">{error}</p>
        <div className="space-x-4">
          <Button onClick={fetchInsightDetail} variant="outline">
            Try Again
          </Button>
          <Button onClick={onBack}>
            Back to Timeline
          </Button>
        </div>
      </div>
    );
  }

  if (!insight) {
    return (
      <div className="text-center py-12">
        <div className="text-gray-400 mb-4">📄</div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">Insight Not Found</h3>
        <p className="text-gray-600 mb-6">The requested session insight could not be found.</p>
        <Button onClick={onBack}>
          Back to Timeline
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card>
        <CardHeader>
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <CardTitle className="text-2xl mb-2">
                {insight.session_title || 'Session Insight'}
              </CardTitle>
              <CardDescription className="space-y-1">
                {insight.session_date && (
                  <div>Session Date: {formatDate(insight.session_date)}</div>
                )}
                <div>Created: {formatDate(insight.created_at)}</div>
                {insight.completed_at && (
                  <div>Completed: {formatDate(insight.completed_at)}</div>
                )}
              </CardDescription>
            </div>
            <div className="flex items-center space-x-3">
              <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                insight.overall_session_quality.toLowerCase() === 'excellent' ? 'bg-green-100 text-green-800' :
                insight.overall_session_quality.toLowerCase() === 'good' ? 'bg-blue-100 text-blue-800' :
                insight.overall_session_quality.toLowerCase() === 'average' ? 'bg-yellow-100 text-yellow-800' :
                'bg-red-100 text-red-800'
              }`}>
                {insight.overall_session_quality}
              </div>
              <Button variant="outline" onClick={onBack}>
                ← Back to Timeline
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <h4 className="font-semibold mb-2">Session Summary</h4>
              <p className="text-gray-700">{insight.session_summary}</p>
            </div>
            
            {insight.key_themes.length > 0 && (
              <div>
                <h4 className="font-semibold mb-2">Key Themes</h4>
                <div className="flex flex-wrap gap-2">
                  {insight.key_themes.map((theme, index) => (
                    <span key={index} className="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full">
                      {theme}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Celebration & Intention */}
      <div className="grid md:grid-cols-2 gap-6">
        {insight.celebration && (
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center">
                🎉 Celebration
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div>
                  <h5 className="font-medium text-sm text-gray-700">Achievement</h5>
                  <p className="text-sm">{insight.celebration.description}</p>
                </div>
                <div>
                  <h5 className="font-medium text-sm text-gray-700">Significance</h5>
                  <p className="text-sm">{insight.celebration.significance}</p>
                </div>
                {insight.celebration.evidence.length > 0 && (
                  <div>
                    <h5 className="font-medium text-sm text-gray-700">Evidence</h5>
                    <ul className="text-sm space-y-1">
                      {insight.celebration.evidence.map((evidence, index) => (
                        <li key={index} className="italic text-gray-600 pl-2 border-l-2 border-gray-200">
                          "{evidence}"
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        )}
        
        {insight.intention && (
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center">
                🎯 Intention
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div>
                  <h5 className="font-medium text-sm text-gray-700">Behavior Change</h5>
                  <p className="text-sm">{insight.intention.behavior_change}</p>
                </div>
                <div className="flex items-center space-x-2">
                  <h5 className="font-medium text-sm text-gray-700">Commitment Level:</h5>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getCommitmentColor(insight.intention.commitment_level)}`}>
                    {insight.intention.commitment_level}
                  </span>
                </div>
                {insight.intention.timeline && (
                  <div>
                    <h5 className="font-medium text-sm text-gray-700">Timeline</h5>
                    <p className="text-sm">{insight.intention.timeline}</p>
                  </div>
                )}
                {insight.intention.support_needed.length > 0 && (
                  <div>
                    <h5 className="font-medium text-sm text-gray-700">Support Needed</h5>
                    <ul className="text-sm space-y-1">
                      {insight.intention.support_needed.map((support, index) => (
                        <li key={index}>• {support}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Client Discoveries */}
      {insight.client_discoveries.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center">
              💡 Client Discoveries
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {insight.client_discoveries.map((discovery, index) => (
                <div key={index} className="border-l-4 border-purple-200 pl-4">
                  <div className="flex items-center space-x-2 mb-2">
                    <h5 className="font-medium">{discovery.insight}</h5>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getDepthColor(discovery.depth_level)}`}>
                      {discovery.depth_level} depth
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mb-2">
                    <strong>Emotional Response:</strong> {discovery.emotional_response}
                  </p>
                  {discovery.evidence.length > 0 && (
                    <div>
                      <h6 className="font-medium text-xs text-gray-700 mb-1">Supporting Evidence:</h6>
                      <ul className="text-xs space-y-1">
                        {discovery.evidence.map((evidence, evidenceIndex) => (
                          <li key={evidenceIndex} className="italic text-gray-600 pl-2 border-l-2 border-gray-200">
                            "{evidence}"
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Goal Progress */}
      {insight.goal_progress.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center">
              📈 Goal Progress
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {insight.goal_progress.map((progress, index) => (
                <div key={index} className="border rounded-lg p-4 bg-gray-50">
                  <div className="flex items-center justify-between mb-2">
                    <h5 className="font-medium">{progress.goal_area}</h5>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getProgressColor(progress.progress_level)}`}>
                      {progress.progress_level}
                    </span>
                  </div>
                  <p className="text-sm text-gray-700 mb-3">{progress.progress_description}</p>
                  
                  {progress.barriers_identified.length > 0 && (
                    <div className="mb-3">
                      <h6 className="font-medium text-sm text-red-700 mb-1">Barriers Identified:</h6>
                      <ul className="text-sm space-y-1">
                        {progress.barriers_identified.map((barrier, barrierIndex) => (
                          <li key={barrierIndex} className="text-red-600">• {barrier}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  {progress.next_steps.length > 0 && (
                    <div>
                      <h6 className="font-medium text-sm text-green-700 mb-1">Next Steps:</h6>
                      <ul className="text-sm space-y-1">
                        {progress.next_steps.map((step, stepIndex) => (
                          <li key={stepIndex} className="text-green-600">• {step}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Powerful Questions */}
      {insight.powerful_questions.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center">
              ❓ Powerful Questions
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {insight.powerful_questions.map((question, index) => (
                <div key={index} className="border-l-4 border-blue-200 pl-4">
                  <div className="flex items-center space-x-2 mb-2">
                    <h5 className="font-medium text-blue-900">"{question.question}"</h5>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getBreakthroughColor(question.breakthrough_level)}`}>
                      {question.breakthrough_level}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mb-2">
                    <strong>Impact:</strong> {question.impact_description}
                  </p>
                  <p className="text-sm text-gray-600">
                    <strong>Client Response:</strong> {question.client_response_summary}
                  </p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Action Items */}
      {insight.action_items.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center">
              ✅ Action Items
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {insight.action_items.map((item, index) => (
                <div key={index} className="flex items-start space-x-3 p-3 border rounded-lg">
                  <div className="flex-1">
                    <p className="font-medium text-sm">{item.action}</p>
                    <div className="flex items-center space-x-4 mt-2 text-xs text-gray-600">
                      {item.timeline && (
                        <span>⏰ {item.timeline}</span>
                      )}
                      {item.accountability_measure && (
                        <span>📊 {item.accountability_measure}</span>
                      )}
                    </div>
                  </div>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getCommitmentColor(item.client_commitment_level)}`}>
                    {item.client_commitment_level}
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Emotional Shifts */}
      {insight.emotional_shifts.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center">
              🌊 Emotional Shifts
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {insight.emotional_shifts.map((shift, index) => (
                <div key={index} className="border rounded-lg p-4 bg-gradient-to-r from-red-50 to-green-50">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-red-700">{shift.initial_state}</span>
                    <span className="text-gray-400">→</span>
                    <span className="text-sm font-medium text-green-700">{shift.final_state}</span>
                  </div>
                  <p className="text-sm text-gray-700 mb-2">{shift.shift_description}</p>
                  <p className="text-xs text-gray-600">
                    <strong>Catalyst:</strong> {shift.catalyst}
                  </p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Values & Beliefs */}
      {insight.values_beliefs.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center">
              🎭 Values & Beliefs
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {insight.values_beliefs.map((item, index) => (
                <div key={index} className="border rounded-lg p-4">
                  <div className="flex items-center space-x-2 mb-2">
                    <h5 className="font-medium">{item.description}</h5>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      item.type === 'Core Value' ? 'bg-blue-100 text-blue-800' :
                      item.type === 'Limiting Belief' ? 'bg-red-100 text-red-800' :
                      'bg-green-100 text-green-800'
                    }`}>
                      {item.type}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mb-2">
                    <strong>Impact on Goals:</strong> {item.impact_on_goals}
                  </p>
                  <p className="text-xs text-gray-500">
                    <strong>Exploration Depth:</strong> {item.exploration_depth}
                  </p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Communication Patterns */}
      {insight.communication_patterns && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center">
              💬 Communication Patterns
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div>
                <h5 className="font-medium text-sm text-gray-700">Processing Style</h5>
                <p className="text-sm">{insight.communication_patterns.processing_style}</p>
              </div>
              
              {insight.communication_patterns.expression_patterns.length > 0 && (
                <div>
                  <h5 className="font-medium text-sm text-gray-700">Expression Patterns</h5>
                  <ul className="text-sm space-y-1">
                    {insight.communication_patterns.expression_patterns.map((pattern, index) => (
                      <li key={index}>• {pattern}</li>
                    ))}
                  </ul>
                </div>
              )}
              
              {insight.communication_patterns.communication_preferences.length > 0 && (
                <div>
                  <h5 className="font-medium text-sm text-gray-700">Communication Preferences</h5>
                  <ul className="text-sm space-y-1">
                    {insight.communication_patterns.communication_preferences.map((preference, index) => (
                      <li key={index}>• {preference}</li>
                    ))}
                  </ul>
                </div>
              )}
              
              {insight.communication_patterns.notable_changes.length > 0 && (
                <div>
                  <h5 className="font-medium text-sm text-gray-700">Notable Changes</h5>
                  <ul className="text-sm space-y-1">
                    {insight.communication_patterns.notable_changes.map((change, index) => (
                      <li key={index}>• {change}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Coaching Presence */}
      {insight.coaching_presence && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center">
              🤝 Coaching Presence
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <h5 className="font-medium text-sm text-gray-700">Client Engagement Level</h5>
                  <p className="text-sm">{insight.coaching_presence.client_engagement_level}</p>
                </div>
                <div>
                  <h5 className="font-medium text-sm text-gray-700">Rapport Quality</h5>
                  <p className="text-sm">{insight.coaching_presence.rapport_quality}</p>
                </div>
              </div>
              
              <div>
                <h5 className="font-medium text-sm text-gray-700">Partnership Dynamics</h5>
                <p className="text-sm">{insight.coaching_presence.partnership_dynamics}</p>
              </div>
              
              {insight.coaching_presence.trust_indicators.length > 0 && (
                <div>
                  <h5 className="font-medium text-sm text-gray-700">Trust Indicators</h5>
                  <ul className="text-sm space-y-1">
                    {insight.coaching_presence.trust_indicators.map((indicator, index) => (
                      <li key={index}>• {indicator}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}