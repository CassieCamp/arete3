"use client";

import { useState } from 'react';
import { X, FileText, MessageSquare } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { SessionEntryForm } from './SessionEntryForm';
import { FreshThoughtEntryForm } from './FreshThoughtEntryForm';
import { GoalSuggestionsModal } from './GoalSuggestionsModal';
import { FreemiumEntryGate } from '../freemium/FreemiumEntryGate';
import { useEntryService, FreemiumStatus, DetectedGoal, EntryFormData } from '@/services/entryService';

interface UnifiedEntryModalProps {
  isOpen: boolean;
  onClose: () => void;
  freemiumStatus: FreemiumStatus;
}

export function UnifiedEntryModal({ isOpen, onClose, freemiumStatus }: UnifiedEntryModalProps) {
  const entryService = useEntryService();
  const [activeTab, setActiveTab] = useState<'session' | 'fresh_thought'>('session');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showGoalSuggestions, setShowGoalSuggestions] = useState(false);
  const [detectedGoals, setDetectedGoals] = useState<DetectedGoal[]>([]);
  const [createdEntryId, setCreatedEntryId] = useState<string>('');
  
  const canCreateEntry = freemiumStatus.has_coach || freemiumStatus.entries_remaining > 0;
  
  const handleEntrySubmit = async (entryData: EntryFormData) => {
    setIsSubmitting(true);
    try {
      const result = await entryService.createEntry({
        ...entryData,
        entry_type: activeTab
      });
      
      setCreatedEntryId(result.id);
      
      // Show goal suggestions if detected
      if (result.detected_goals && result.detected_goals.length > 0) {
        setDetectedGoals(result.detected_goals);
        setShowGoalSuggestions(true);
      } else {
        onClose();
        // Show success message (you might want to use a toast library)
        alert(`${activeTab === 'session' ? 'Session' : 'Thought'} added successfully!`);
      }
    } catch (error: any) {
      console.error('Error creating entry:', error);
      alert(error.message || 'Failed to create entry. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };
  
  const handleGoalSuggestionsComplete = () => {
    setShowGoalSuggestions(false);
    onClose();
    alert('Entry and destinations added successfully!');
  };
  
  if (!isOpen) return null;
  
  return (
    <>
      <Dialog open={isOpen} onOpenChange={onClose}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-hidden">
          {/* Header */}
          <DialogHeader>
            <DialogTitle>Add Entry</DialogTitle>
          </DialogHeader>
          
          {/* Freemium Gate Check */}
          {!canCreateEntry ? (
            <FreemiumEntryGate 
              freemiumStatus={freemiumStatus}
              onClose={onClose}
            />
          ) : (
            <>
              {/* Tab Navigation */}
              <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as 'session' | 'fresh_thought')}>
                <TabsList className="grid w-full grid-cols-2">
                  <TabsTrigger value="session" className="flex items-center space-x-2">
                    <FileText className="w-4 h-4" />
                    <span>Session</span>
                  </TabsTrigger>
                  <TabsTrigger value="fresh_thought" className="flex items-center space-x-2">
                    <MessageSquare className="w-4 h-4" />
                    <span>Fresh Thoughts</span>
                  </TabsTrigger>
                </TabsList>
                
                {/* Tab Content */}
                <div className="overflow-y-auto max-h-[60vh] p-1">
                  <TabsContent value="session" className="mt-4">
                    <SessionEntryForm 
                      onSubmit={handleEntrySubmit}
                      isSubmitting={isSubmitting}
                      freemiumStatus={freemiumStatus}
                    />
                  </TabsContent>
                  
                  <TabsContent value="fresh_thought" className="mt-4">
                    <FreshThoughtEntryForm 
                      onSubmit={handleEntrySubmit}
                      isSubmitting={isSubmitting}
                      freemiumStatus={freemiumStatus}
                    />
                  </TabsContent>
                </div>
              </Tabs>
            </>
          )}
        </DialogContent>
      </Dialog>
      
      {/* Goal Suggestions Modal */}
      <GoalSuggestionsModal
        isOpen={showGoalSuggestions}
        onClose={handleGoalSuggestionsComplete}
        entryId={createdEntryId}
        detectedGoals={detectedGoals}
      />
    </>
  );
}