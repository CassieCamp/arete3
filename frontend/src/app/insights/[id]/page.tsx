"use client";

import { useParams, useRouter } from 'next/navigation';
import { PageHeader } from "@/components/navigation/NavigationUtils";
import { useSessionInsight } from "@/hooks/useSessionInsight";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { X } from "lucide-react";

export default function DynamicInsightPage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;
  const { insight, loading, error, refetch } = useSessionInsight(id);

  const handleClose = () => {
    router.push('/journey');
  };

  // Loading state
  if (loading) {
    return (
      <div className="min-h-screen bg-background">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-muted-foreground">Loading session insight...</p>
          </div>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="min-h-screen bg-background">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
          <div className="text-center py-12">
            <div className="text-6xl mb-4">⚠️</div>
            <h1 className="text-2xl font-bold text-foreground mb-2">
              Error Loading Insight
            </h1>
            <p className="text-red-600 mb-4">{error}</p>
            <Button onClick={refetch} variant="outline">
              Try Again
            </Button>
          </div>
        </div>
      </div>
    );
  }

  // No insight found
  if (!insight) {
    return (
      <div className="min-h-screen bg-background">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
          <div className="text-center py-12">
            <div className="text-6xl mb-4">🔍</div>
            <h1 className="text-2xl font-bold text-foreground mb-2">
              Insight Not Found
            </h1>
            <p className="text-muted-foreground mb-4">
              The session insight you're looking for could not be found.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
        {/* Header Section */}
        <div className="flex flex-col sm:flex-row sm:justify-between sm:items-start gap-4 mb-8 sm:mb-12">
          <div className="flex-1">
            <h1 className="text-2xl sm:text-3xl font-bold text-foreground mb-2">
              {insight.session_title || 'Session Insight'}
            </h1>
            <div className="flex items-center gap-4 text-sm text-muted-foreground">
              {insight.session_date && (
                <span>📅 {new Date(insight.session_date).toLocaleDateString()}</span>
              )}
            </div>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleClose}
            className="p-2 hover:bg-muted rounded-lg transition-colors self-start sm:self-auto"
            aria-label="Close and return to Journey"
          >
            <X className="h-5 w-5" />
          </Button>
        </div>

        <div className="max-w-4xl mx-auto space-y-8 sm:space-y-12">
          {/* Key Insights & Discoveries */}
          {insight.client_discoveries && insight.client_discoveries.length > 0 && (
            <section className="space-y-4 sm:space-y-6">
              <div className="flex items-center gap-3 mb-6 sm:mb-8">
                <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                  <span className="text-lg">💡</span>
                </div>
                <h2 className="text-lg font-medium text-muted-foreground">Self Discovery</h2>
              </div>
              <div className="space-y-6 sm:space-y-8">
                {insight.client_discoveries.map((discovery, index) => (
                  <div key={index} className="group">
                    <div className="bg-background border border-border rounded-lg p-4 sm:p-6 lg:p-8 hover:shadow-md transition-shadow">
                      <blockquote className="text-lg sm:text-xl lg:text-2xl font-medium text-foreground leading-relaxed mb-3 sm:mb-4">
                        "{discovery.insight}"
                      </blockquote>
                      <p className="text-sm sm:text-base text-muted-foreground">
                        <span className="font-medium">How this felt:</span> {discovery.emotional_response}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Celebration */}
          {insight.celebration && (
            <section className="space-y-4 sm:space-y-6">
              <div className="flex items-center gap-3 mb-6 sm:mb-8">
                <div className="w-8 h-8 rounded-full bg-secondary/10 flex items-center justify-center">
                  <span className="text-lg">🎉</span>
                </div>
                <h2 className="text-lg font-medium text-muted-foreground">Celebration</h2>
              </div>
              <div className="bg-background border border-border rounded-lg p-4 sm:p-6 lg:p-8 hover:shadow-md transition-shadow">
                <blockquote className="text-lg sm:text-xl lg:text-2xl font-medium text-foreground leading-relaxed mb-3 sm:mb-4">
                  "{insight.celebration.description}"
                </blockquote>
                <p className="text-sm sm:text-base text-muted-foreground">{insight.celebration.significance}</p>
              </div>
            </section>
          )}

          {/* Action Commitments */}
          {insight.action_items && insight.action_items.length > 0 && (
            <section className="space-y-4 sm:space-y-6">
              <div className="flex items-center gap-3 mb-6 sm:mb-8">
                <div className="w-8 h-8 rounded-full bg-accent/10 flex items-center justify-center">
                  <span className="text-lg">🎯</span>
                </div>
                <h2 className="text-lg font-medium text-muted-foreground">Action Commitments</h2>
              </div>
              <div className="space-y-4 sm:space-y-6">
                {insight.action_items.map((item, index) => (
                  <div key={index} className="bg-background border border-border rounded-lg p-4 sm:p-6 lg:p-8 hover:shadow-md transition-shadow">
                    <blockquote className="text-lg sm:text-xl lg:text-2xl font-medium text-foreground leading-relaxed mb-4 sm:mb-6">
                      "{item.action}"
                    </blockquote>
                    <div className="flex flex-col sm:flex-row sm:flex-wrap gap-3 sm:gap-6 text-sm text-muted-foreground">
                      {item.timeline && (
                        <div className="flex items-center gap-2">
                          <span className="w-2 h-2 rounded-full bg-accent flex-shrink-0"></span>
                          <span><strong>By when:</strong> {item.timeline}</span>
                        </div>
                      )}
                      {item.accountability_measure && (
                        <div className="flex items-center gap-2">
                          <span className="w-2 h-2 rounded-full bg-accent flex-shrink-0"></span>
                          <span><strong>How you'll track progress:</strong> {item.accountability_measure}</span>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Future Intentions */}
          {insight.intention && (
            <section className="space-y-4 sm:space-y-6">
              <div className="flex items-center gap-3 mb-6 sm:mb-8">
                <div className="w-8 h-8 rounded-full bg-chart-1/10 flex items-center justify-center">
                  <span className="text-lg">🌟</span>
                </div>
                <h2 className="text-lg font-medium text-muted-foreground">Future Intentions</h2>
              </div>
              <div className="bg-background border border-border rounded-lg p-4 sm:p-6 lg:p-8 hover:shadow-md transition-shadow">
                <blockquote className="text-lg sm:text-xl lg:text-2xl font-medium text-foreground leading-relaxed mb-4 sm:mb-6">
                  "{insight.intention.behavior_change}"
                </blockquote>
                <div className="space-y-3 sm:space-y-4">
                  {insight.intention.timeline && (
                    <div className="flex items-center gap-2 text-sm sm:text-base text-muted-foreground">
                      <span className="w-2 h-2 rounded-full bg-chart-1 flex-shrink-0"></span>
                      <span><strong>Timeline:</strong> {insight.intention.timeline}</span>
                    </div>
                  )}
                  {insight.intention.support_needed && insight.intention.support_needed.length > 0 && (
                    <div>
                      <p className="font-medium text-foreground mb-3 text-sm sm:text-base">Support that would help:</p>
                      <ul className="space-y-2">
                        {insight.intention.support_needed.map((support, index) => (
                          <li key={index} className="flex items-start gap-2 text-sm sm:text-base text-muted-foreground">
                            <span className="w-2 h-2 rounded-full bg-chart-1 mt-2 flex-shrink-0"></span>
                            <span>{support}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            </section>
          )}

          {/* Powerful Questions */}
          {insight.powerful_questions && insight.powerful_questions.length > 0 && (
            <section className="space-y-4 sm:space-y-6">
              <div className="flex items-center gap-3 mb-6 sm:mb-8">
                <div className="w-8 h-8 rounded-full bg-chart-2/10 flex items-center justify-center">
                  <span className="text-lg">🤔</span>
                </div>
                <h2 className="text-lg font-medium text-muted-foreground">Powerful Questions</h2>
              </div>
              <div className="space-y-6 sm:space-y-8">
                {insight.powerful_questions.map((question, index) => (
                  <div key={index} className="bg-background border border-border rounded-lg p-4 sm:p-6 lg:p-8 hover:shadow-md transition-shadow">
                    <blockquote className="text-lg sm:text-xl lg:text-2xl font-medium text-foreground italic leading-relaxed mb-3 sm:mb-4">
                      "{question.question}"
                    </blockquote>
                    <p className="text-sm sm:text-base text-muted-foreground mb-3 sm:mb-4">{question.impact_description}</p>
                    {question.client_response_summary && (
                      <div className="bg-muted/30 rounded-lg p-3 sm:p-4 border-l-4 border-chart-2">
                        <p className="text-sm sm:text-base text-foreground">
                          <span className="font-medium">Your reflection:</span> {question.client_response_summary}
                        </p>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Session Overview */}
          <section className="space-y-4 sm:space-y-6 border-t border-border pt-8 sm:pt-12">
            <div className="flex items-center gap-3 mb-6 sm:mb-8">
              <div className="w-8 h-8 rounded-full bg-muted/50 flex items-center justify-center">
                <span className="text-lg">📝</span>
              </div>
              <h2 className="text-lg font-medium text-muted-foreground">Session Overview</h2>
            </div>
            <div className="bg-muted/20 rounded-lg p-4 sm:p-6 lg:p-8">
              <p className="text-base sm:text-lg text-foreground leading-relaxed mb-4 sm:mb-6">
                {insight.session_summary || 'No summary available'}
              </p>
              {insight.key_themes && insight.key_themes.length > 0 && (
                <div>
                  <p className="font-medium text-foreground mb-3 sm:mb-4 text-sm sm:text-base">Key themes we explored:</p>
                  <div className="flex flex-wrap gap-2 sm:gap-3">
                    {insight.key_themes.map((theme, index) => (
                      <span key={index} className="bg-background px-3 sm:px-4 py-1.5 sm:py-2 rounded-full text-xs sm:text-sm text-foreground border border-border">
                        {theme}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}