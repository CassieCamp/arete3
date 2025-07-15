import { formatDistanceToNow } from 'date-fns';
import { Lightbulb, ChevronRight } from 'lucide-react';
import { LEADERSHIP_CATEGORIES } from '../../config/leadershipCategories';
import CategoryBadge from './CategoryBadge';
import React from 'react';

// --- Placeholder UI Components (assuming they exist in the actual project) ---
const Card = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(({ className, ...props }, ref) => (
  <div ref={ref} className={`rounded-lg border bg-card text-card-foreground shadow-sm ${className}`} {...props} />
));
Card.displayName = "Card";

const CardHeader = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(({ className, ...props }, ref) => (
  <div ref={ref} className={`flex flex-col space-y-1.5 p-6 ${className}`} {...props} />
));
CardHeader.displayName = "CardHeader";

const CardContent = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(({ className, ...props }, ref) => (
  <div ref={ref} className={`p-6 pt-0 ${className}`} {...props} />
));
CardContent.displayName = "CardContent";

const CardFooter = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(({ className, ...props }, ref) => (
  <div ref={ref} className={`flex items-center p-6 pt-0 ${className}`} {...props} />
));
CardFooter.displayName = "CardFooter";
// --- End Placeholder UI Components ---

// --- Placeholder Types and Utils ---
interface Insight {
  id: string;
  summary: string;
  created_at: string;
  reflection?: { type: string };
  categories: string[];
  key_points?: string[];
  breakthrough_moment?: string;
  confidence_score: number;
  action_items?: any[];
}

const getReflectionTypeLabel = (type?: string) => {
  if (!type) return 'Reflection';
  return type.charAt(0).toUpperCase() + type.slice(1);
};
// --- End Placeholder Types and Utils ---


interface InsightCardProps {
  insight: Insight;
  onExpand: (insight: Insight) => void;
  onCategoryFilter: (category: string) => void;
}

const InsightCard = ({ insight, onExpand, onCategoryFilter }: InsightCardProps) => {
  return (
    <Card
      className="hover:shadow-md transition-all duration-200 cursor-pointer group border-border"
      style={{
        backgroundColor: 'oklch(0.9583 0.0111 89.7230) !important',
        color: 'oklch(0.2177 0.0356 251.2935) !important'
      }}
      onClick={() => {
        onExpand(insight);
      }}
    >
      <CardHeader>
        <div className="flex justify-between items-start gap-4">
          <div className="flex-1 min-w-0">
            <h3 className="font-semibold text-lg text-card-foreground mb-2 line-clamp-2" style={{ color: 'oklch(0.2177 0.0356 251.2935)' }}>
              {insight.summary}
            </h3>
            <div className="flex items-center gap-2 text-sm text-muted-foreground mb-3" style={{ color: 'oklch(0.4855 0 0)' }}>
              <span>{formatDistanceToNow(new Date(insight.created_at))} ago</span>
              <span>•</span>
              <span>From {getReflectionTypeLabel(insight.reflection?.type)}</span>
            </div>
          </div>
          
          <div className="flex flex-wrap justify-end gap-1 ml-2">
            {insight.categories.map(categoryKey => {
              const category = LEADERSHIP_CATEGORIES.find(c => c.key === categoryKey);
              if (!category) return null;
              
              return (
                <CategoryBadge
                  key={categoryKey}
                  category={category}
                  size="sm"
                  onClick={(e) => {
                    e.stopPropagation();
                    onCategoryFilter(categoryKey);
                  }}
                />
              );
            })}
          </div>
        </div>
      </CardHeader>
      
      <CardContent>
        <div className="space-y-3">
          {/* Key Points Preview */}
          {insight.key_points?.slice(0, 2).map((point, idx) => (
            <div key={idx} className="flex items-start gap-3">
              <div className="w-1.5 h-1.5 bg-primary rounded-full mt-2 flex-shrink-0" />
              <p className="text-sm text-muted-foreground line-clamp-2" style={{ color: 'oklch(0.4855 0 0)' }}>{point}</p>
            </div>
          ))}
          
          {/* Breakthrough Moment */}
          {insight.breakthrough_moment && (
            <div className="mt-4 p-3 bg-accent/10 rounded-lg border-l-4 border-accent">
              <div className="flex items-start gap-2">
                <Lightbulb className="w-4 h-4 text-accent-foreground mt-0.5 flex-shrink-0" style={{ color: 'oklch(0.6087 0.1830 38.3621)' }} />
                <p className="text-sm text-accent-foreground font-medium" style={{ color: 'oklch(0.2177 0.0356 251.2935)' }}>
                  {insight.breakthrough_moment}
                </p>
              </div>
            </div>
          )}
        </div>
      </CardContent>
      
      <CardFooter>
        <div className="flex justify-between items-center w-full">
          <div className="flex items-center gap-2 text-xs text-muted-foreground" style={{ color: 'oklch(0.4855 0 0)' }}>
            <span>AI Confidence: {Math.round(insight.confidence_score * 100)}%</span>
            {insight.action_items && insight.action_items.length > 0 && (
              <>
                <span>•</span>
                <span>{insight.action_items.length} action{insight.action_items.length !== 1 ? 's' : ''}</span>
              </>
            )}
          </div>
          <ChevronRight className="w-4 h-4 text-muted-foreground group-hover:text-foreground transition-colors" style={{ color: 'oklch(0.4855 0 0)' }} />
        </div>
      </CardFooter>
    </Card>
  );
};

export default InsightCard;