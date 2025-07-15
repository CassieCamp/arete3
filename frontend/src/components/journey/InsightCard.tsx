'use client';

import React, { useState, useCallback } from 'react';
import { JourneyFeedItem, InsightItem, ReflectionItem } from '@/hooks/journey/useAdvancedInsights';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter, CardAction } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  Star, 
  Eye, 
  Calendar, 
  Target, 
  ChevronDown, 
  ChevronUp, 
  ExternalLink,
  BookOpen,
  Lightbulb,
  MessageSquare,
  ThumbsUp,
  ThumbsDown,
  MoreHorizontal
} from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

interface InsightCardProps {
  insight: JourneyFeedItem;
  className?: string;
  onFavoriteToggle?: (id: string, isFavorite: boolean) => void;
  onRatingChange?: (id: string, rating: number) => void;
  onViewSource?: (sourceId: string) => void;
}

export function InsightCard({ 
  insight, 
  className = '',
  onFavoriteToggle,
  onRatingChange,
  onViewSource
}: InsightCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [isUpdatingFavorite, setIsUpdatingFavorite] = useState(false);

  const isInsight = insight.type === 'insight';
  const insightData = isInsight ? (insight as InsightItem) : null;
  const reflectionData = !isInsight ? (insight as ReflectionItem) : null;

  // Handle favorite toggle
  const handleFavoriteToggle = useCallback(async () => {
    if (!isInsight || !insightData || !onFavoriteToggle) return;
    
    setIsUpdatingFavorite(true);
    try {
      await onFavoriteToggle(insight.id, !insightData.is_favorite);
    } catch (error) {
      console.error('Failed to toggle favorite:', error);
    } finally {
      setIsUpdatingFavorite(false);
    }
  }, [isInsight, insightData, insight.id, onFavoriteToggle]);

  // Handle rating change
  const handleRatingChange = useCallback((rating: number) => {
    if (!isInsight || !onRatingChange) return;
    onRatingChange(insight.id, rating);
  }, [isInsight, insight.id, onRatingChange]);

  // Format confidence score
  const formatConfidence = (score?: number) => {
    if (!score) return null;
    return `${Math.round(score * 100)}%`;
  };

  // Get status color
  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'approved':
      case 'completed':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      case 'pending':
      case 'processing':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
      case 'rejected':
      case 'failed':
        return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200';
    }
  };

  // Truncate text
  const truncateText = (text: string, maxLength: number = 200) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  return (
    <Card className={`group hover:shadow-md transition-all duration-200 ${className}`}>
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex-1 min-w-0">
            <CardTitle className="flex items-center gap-2 text-lg">
              {isInsight ? (
                <Lightbulb className="w-5 h-5 text-primary flex-shrink-0" />
              ) : (
                <MessageSquare className="w-5 h-5 text-secondary flex-shrink-0" />
              )}
              <span className="truncate">{insight.title}</span>
            </CardTitle>
            
            <CardDescription className="mt-2 flex flex-wrap items-center gap-3 text-sm">
              <span className="flex items-center gap-1">
                <Calendar className="w-4 h-4" />
                {formatDistanceToNow(new Date(insight.created_at), { addSuffix: true })}
              </span>
              
              {isInsight && insightData?.confidence_score && (
                <span className="flex items-center gap-1">
                  <Target className="w-4 h-4" />
                  {formatConfidence(insightData.confidence_score)} confidence
                </span>
              )}
              
              {isInsight && insightData && insightData.view_count > 0 && (
                <span className="flex items-center gap-1">
                  <Eye className="w-4 h-4" />
                  {insightData.view_count} views
                </span>
              )}

              {reflectionData && (
                <span className="flex items-center gap-1">
                  <Lightbulb className="w-4 h-4" />
                  {reflectionData.insight_count} insights
                </span>
              )}
            </CardDescription>
          </div>

          <CardAction>
            <div className="flex items-center gap-2">
              {/* Favorite Button (Insights only) */}
              {isInsight && insightData && (
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={handleFavoriteToggle}
                  disabled={isUpdatingFavorite}
                  className={`transition-colors ${
                    insightData.is_favorite 
                      ? 'text-yellow-500 hover:text-yellow-600' 
                      : 'text-muted-foreground hover:text-yellow-500'
                  }`}
                >
                  <Star 
                    className={`w-4 h-4 ${insightData.is_favorite ? 'fill-current' : ''}`} 
                  />
                </Button>
              )}

              {/* More Actions */}
              <Button variant="ghost" size="icon" className="opacity-0 group-hover:opacity-100 transition-opacity">
                <MoreHorizontal className="w-4 h-4" />
              </Button>
            </div>
          </CardAction>
        </div>

        {/* Categories and Tags */}
        <div className="flex flex-wrap gap-2 mt-3">
          {/* Category Badge */}
          {isInsight && insightData?.category && (
            <Badge variant="secondary" className="text-xs">
              {insightData.category}
            </Badge>
          )}
          
          {reflectionData?.categories.map(category => (
            <Badge key={category} variant="secondary" className="text-xs">
              {category}
            </Badge>
          ))}

          {/* Status Badge */}
          {isInsight && insightData?.review_status && (
            <Badge 
              className={`text-xs ${getStatusColor(insightData.review_status)}`}
            >
              {insightData.review_status}
            </Badge>
          )}

          {reflectionData?.processing_status && (
            <Badge 
              className={`text-xs ${getStatusColor(reflectionData.processing_status)}`}
            >
              {reflectionData.processing_status}
            </Badge>
          )}

          {/* Actionable Badge */}
          {isInsight && insightData?.is_actionable && (
            <Badge variant="outline" className="text-xs flex items-center gap-1">
              <Target className="w-3 h-3" />
              Actionable
            </Badge>
          )}
        </div>
      </CardHeader>

      <CardContent>
        {/* Summary/Description */}
        <div className="space-y-3">
          {isInsight && insightData?.summary && (
            <p className="text-sm text-muted-foreground leading-relaxed">
              {isExpanded ? insightData.summary : truncateText(insightData.summary)}
            </p>
          )}

          {reflectionData?.description && (
            <p className="text-sm text-muted-foreground leading-relaxed">
              {isExpanded ? reflectionData.description : truncateText(reflectionData.description)}
            </p>
          )}

          {/* Content (when expanded) */}
          {isExpanded && (
            <div className="space-y-3 pt-3 border-t border-border">
              {isInsight && insightData?.content && (
                <div>
                  <h4 className="font-medium text-sm mb-2">Full Content</h4>
                  <p className="text-sm leading-relaxed whitespace-pre-wrap">
                    {insightData.content}
                  </p>
                </div>
              )}

              {reflectionData?.content && (
                <div>
                  <h4 className="font-medium text-sm mb-2">Reflection Content</h4>
                  <p className="text-sm leading-relaxed whitespace-pre-wrap">
                    {reflectionData.content}
                  </p>
                </div>
              )}

              {/* Suggested Actions */}
              {isInsight && insightData?.suggested_actions && insightData.suggested_actions.length > 0 && (
                <div>
                  <h4 className="font-medium text-sm mb-2 flex items-center gap-1">
                    <Target className="w-4 h-4" />
                    Suggested Actions
                  </h4>
                  <ul className="space-y-1">
                    {insightData.suggested_actions.map((action, index) => (
                      <li key={index} className="text-sm text-muted-foreground flex items-start gap-2">
                        <span className="w-1.5 h-1.5 bg-primary rounded-full mt-2 flex-shrink-0" />
                        {action}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Source Information */}
              {isInsight && insightData?.source_title && (
                <div>
                  <h4 className="font-medium text-sm mb-2 flex items-center gap-1">
                    <BookOpen className="w-4 h-4" />
                    Source
                  </h4>
                  <div className="bg-muted/50 rounded-lg p-3">
                    <p className="font-medium text-sm">{insightData.source_title}</p>
                    {insightData.source_excerpt && (
                      <p className="text-xs text-muted-foreground mt-1">
                        "{insightData.source_excerpt}"
                      </p>
                    )}
                    {onViewSource && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => onViewSource(insightData.source_id)}
                        className="mt-2 h-auto py-1 px-2 text-xs"
                      >
                        <ExternalLink className="w-3 h-3 mr-1" />
                        View Source
                      </Button>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Tags */}
        {(() => {
          const tags = isInsight ? insightData?.tags : reflectionData?.tags;
          return tags && tags.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-4">
              {tags.map(tag => (
                <Badge key={tag} variant="outline" className="text-xs">
                  #{tag}
                </Badge>
              ))}
            </div>
          );
        })()}
      </CardContent>

      <CardFooter className="flex items-center justify-between">
        {/* Expand/Collapse Button */}
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setIsExpanded(!isExpanded)}
          className="flex items-center gap-1 text-muted-foreground hover:text-foreground"
        >
          {isExpanded ? (
            <>
              <ChevronUp className="w-4 h-4" />
              Show less
            </>
          ) : (
            <>
              <ChevronDown className="w-4 h-4" />
              Show more
            </>
          )}
        </Button>

        {/* Rating (Insights only) */}
        {isInsight && insightData && (
          <div className="flex items-center gap-1">
            {insightData.user_rating && (
              <span className="text-xs text-muted-foreground mr-2">
                Rated {insightData.user_rating}/5
              </span>
            )}
            <Button
              variant="ghost"
              size="icon"
              onClick={() => handleRatingChange(5)}
              className="w-6 h-6 text-muted-foreground hover:text-green-600"
            >
              <ThumbsUp className="w-3 h-3" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => handleRatingChange(1)}
              className="w-6 h-6 text-muted-foreground hover:text-red-600"
            >
              <ThumbsDown className="w-3 h-3" />
            </Button>
          </div>
        )}
      </CardFooter>
    </Card>
  );
}