import React, { useState } from 'react';
import { ChevronDown, ChevronUp, FileText, ExternalLink } from 'lucide-react';

interface InsightCardProps {
  reflection: {
    id: string;
    title: string; // AI-generated document title
    original_filename: string;
    upload_date: string;
    insights_by_category: {
      understanding_myself?: string[];
      navigating_relationships?: string[];
      optimizing_performance?: string[];
      making_progress?: string[];
    };
    source_file_path?: string;
  };
}

const CATEGORY_CONFIG = {
  understanding_myself: {
    label: "🔍 Understanding Myself",
    description: "Self-awareness, emotional shifts, values alignment"
  },
  navigating_relationships: {
    label: "🤝 Navigating Relationships", 
    description: "Interpersonal growth, politics, leadership influence"
  },
  optimizing_performance: {
    label: "⚡ Optimizing Performance",
    description: "Energy patterns, strengths, effectiveness"  
  },
  making_progress: {
    label: "🎯 Making Progress",
    description: "Goals, accountability, wins, forward motion"
  }
};

export const InsightCard: React.FC<InsightCardProps> = ({ reflection }) => {
  // Add safe defaults for all properties
  const safeReflection = {
    ...reflection,
    title: reflection?.title || 'Untitled Document',
    upload_date: reflection?.upload_date || new Date().toISOString(),
    original_filename: reflection?.original_filename || 'Unknown file',
    insights_by_category: reflection?.insights_by_category || {}
  };

  const [isExpanded, setIsExpanded] = useState(false);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric', 
      year: 'numeric'
    });
  };

  return (
    <div 
      className="bg-background/10 backdrop-blur-sm border border-border/20 rounded-lg transition-all duration-300 hover:bg-background/15 cursor-pointer"
      onClick={() => setIsExpanded(!isExpanded)}
    >
      {/* Header - Always Visible */}
      <div className="p-4">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <FileText className="w-4 h-4 text-primary" />
              <h3 className="text-foreground text-base font-semibold">
                {safeReflection.title}
              </h3>
            </div>
            <p className="text-muted-foreground text-sm mb-2">
              {formatDate(safeReflection.upload_date)}
            </p>
            <p className="text-muted-foreground text-xs">
              {safeReflection.original_filename}
            </p>
          </div>
          <div className="ml-4 text-muted-foreground">
            {isExpanded ? (
              <ChevronUp className="w-4 h-4" />
            ) : (
              <ChevronDown className="w-4 h-4" />
            )}
          </div>
        </div>
      </div>

      {/* Expanded Content - Document Insights by Category */}
      <div 
        className={`overflow-hidden transition-all duration-300 ${
          isExpanded ? 'max-h-[600px] opacity-100' : 'max-h-0 opacity-0'
        }`}
      >
        <div className="px-4 pb-4 border-t border-border/20 pt-4 bg-background/5">
          
          {/* Insights by Category */}
          {Object.entries(CATEGORY_CONFIG).map(([categoryKey, config]) => {
            const categoryInsights = safeReflection.insights_by_category[categoryKey as keyof typeof safeReflection.insights_by_category];
            
            if (!categoryInsights || categoryInsights.length === 0) return null;
            
            return (
              <div key={categoryKey} className="mb-6 last:mb-4">
                <h4 className="text-white font-bold text-sm mb-2 flex items-center gap-2">
                  {config.label}
                </h4>
                <ul className="space-y-2 ml-4">
                  {categoryInsights.map((insight, index) => (
                    <li key={index} className="text-white/90 text-sm flex items-start leading-relaxed">
                      <span className="w-1.5 h-1.5 bg-blue-400 rounded-full mt-2 mr-3 flex-shrink-0" />
                      {insight}
                    </li>
                  ))}
                </ul>
              </div>
            );
          })}

          {/* Source File Link */}
          {safeReflection.source_file_path && (
            <div className="pt-4 border-t border-border/10">
              <button className="flex items-center gap-2 text-primary hover:text-primary/80 text-sm transition-colors">
                <ExternalLink className="w-3 h-3" />
                View original document
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};