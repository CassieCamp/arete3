"use client";

import { useState, useEffect } from 'react';
import { Plus, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { UnifiedEntryModal } from './UnifiedEntryModal';
import { useEntryService, FreemiumStatus } from '@/services/entryService';

interface UnifiedEntryCTAProps {
  freemiumStatus: FreemiumStatus;
  showTooltip?: boolean;
  onTooltipDismiss?: () => void;
  className?: string;
}

export function UnifiedEntryCTA({
  freemiumStatus: initialFreemiumStatus,
  showTooltip = false,
  onTooltipDismiss,
  className = ""
}: UnifiedEntryCTAProps) {
  const entryService = useEntryService();
  const [showEntryModal, setShowEntryModal] = useState(false);
  const [freemiumStatus, setFreemiumStatus] = useState<FreemiumStatus>(initialFreemiumStatus);
  const [isLoadingStatus, setIsLoadingStatus] = useState(false);
  
  // Fetch fresh freemium status when modal opens
  useEffect(() => {
    if (showEntryModal && !isLoadingStatus) {
      fetchFreemiumStatus();
    }
  }, [showEntryModal]);
  
  const fetchFreemiumStatus = async () => {
    setIsLoadingStatus(true);
    try {
      const status = await entryService.getFreemiumStatus();
      setFreemiumStatus(status);
    } catch (error) {
      console.error('Error fetching freemium status:', error);
    } finally {
      setIsLoadingStatus(false);
    }
  };
  
  const canCreateEntry = freemiumStatus.has_coach || freemiumStatus.entries_remaining > 0;
  
  return (
    <div className={`relative ${className}`}>
      {/* Main CTA Button */}
      <Card className="w-full">
        <CardContent className="p-0">
          <Button
            variant="ghost"
            onClick={() => setShowEntryModal(true)}
            disabled={!canCreateEntry}
            className={`w-full p-6 h-auto border-2 border-dashed transition-all duration-200 ${
              canCreateEntry
                ? 'border-primary/30 bg-primary/5 hover:border-primary/50 hover:bg-primary/10'
                : 'border-muted-foreground/30 bg-muted/20 cursor-not-allowed'
            }`}
          >
            <div className="text-center">
              <Plus className={`w-8 h-8 mx-auto mb-2 ${
                canCreateEntry ? 'text-primary' : 'text-muted-foreground'
              }`} />
              <h3 className={`text-lg font-medium mb-1 ${
                canCreateEntry ? 'text-foreground' : 'text-muted-foreground'
              }`}>
                Add Entry
              </h3>
              <p className={`text-sm ${
                canCreateEntry ? 'text-muted-foreground' : 'text-muted-foreground/70'
              }`}>
                Share a recent session or fresh thought
              </p>
              
              {/* Freemium Warning */}
              {!freemiumStatus.has_coach && (
                <div className="mt-3 text-xs text-orange-600 dark:text-orange-400">
                  {freemiumStatus.entries_remaining} free entries remaining
                </div>
              )}
            </div>
          </Button>
        </CardContent>
      </Card>
      
      {/* Tooltip for first-time users */}
      {showTooltip && (
        <div className="absolute -top-16 left-1/2 transform -translate-x-1/2 z-10">
          <div className="bg-popover text-popover-foreground text-sm rounded-lg px-4 py-2 whitespace-nowrap shadow-lg border">
            Tap here to add your first entry!
            <Button
              variant="ghost"
              size="sm"
              onClick={onTooltipDismiss}
              className="ml-2 p-0 h-auto text-muted-foreground hover:text-foreground"
            >
              <X className="w-3 h-3" />
            </Button>
            <div className="absolute top-full left-1/2 transform -translate-x-1/2">
              <div className="border-4 border-transparent border-t-popover"></div>
            </div>
          </div>
        </div>
      )}
      
      {/* Unified Entry Modal */}
      <UnifiedEntryModal
        isOpen={showEntryModal}
        onClose={() => setShowEntryModal(false)}
        freemiumStatus={freemiumStatus}
      />
    </div>
  );
}

// Simple version without freemium logic for basic use
export function SimpleEntryCTA({
  onClick,
  className = ""
}: {
  onClick?: () => void;
  className?: string;
}) {
  const defaultFreemiumStatus: FreemiumStatus = {
    has_coach: true,
    entries_count: 0,
    max_free_entries: 3,
    entries_remaining: 3,
    can_create_entries: true,
    can_access_insights: true,
    is_freemium: false
  };

  return (
    <UnifiedEntryCTA
      freemiumStatus={defaultFreemiumStatus}
      showTooltip={false}
      className={className}
    />
  );
}