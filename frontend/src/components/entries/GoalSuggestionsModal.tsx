"use client";

import { useState } from 'react';
import { X, Target, Check } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { useEntryService, DetectedGoal } from '@/services/entryService';
import { useToast } from '@/hooks/use-toast';

interface GoalSuggestionsModalProps {
  isOpen: boolean;
  onClose: () => void;
  entryId: string;
  detectedGoals: DetectedGoal[];
}

export function GoalSuggestionsModal({
  isOpen,
  onClose,
  entryId,
  detectedGoals
}: GoalSuggestionsModalProps) {
  const entryService = useEntryService();
  const { toast } = useToast();
  const [selectedGoals, setSelectedGoals] = useState<number[]>([]);
  const [isAccepting, setIsAccepting] = useState(false);

  const handleGoalToggle = (index: number) => {
    setSelectedGoals(prev => 
      prev.includes(index) 
        ? prev.filter(i => i !== index)
        : [...prev, index]
    );
  };

  const handleAcceptGoals = async () => {
    if (selectedGoals.length === 0) {
      onClose();
      return;
    }

    setIsAccepting(true);
    try {
      await entryService.acceptGoals(entryId, selectedGoals);
      
      toast({
        title: "Goal Added",
        description: "Successfully added the new goal."
      });
      onClose();
    } catch (error) {
      console.error('Error accepting goals:', error);
      toast({
        title: "Error",
        description: "Failed to accept goals. Please try again.",
        variant: "destructive"
      });
    } finally {
      setIsAccepting(false);
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-green-600 bg-green-100';
    if (confidence >= 0.6) return 'text-yellow-600 bg-yellow-100';
    return 'text-orange-600 bg-orange-100';
  };

  const getConfidenceLabel = (confidence: number) => {
    if (confidence >= 0.8) return 'High';
    if (confidence >= 0.6) return 'Medium';
    return 'Low';
  };

  if (!isOpen) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-hidden">
        <DialogHeader>
          <DialogTitle className="flex items-center space-x-2">
            <Target className="w-5 h-5 text-blue-600" />
            <span>Detected Goals</span>
          </DialogTitle>
        </DialogHeader>
        
        <div className="space-y-4">
          <p className="text-gray-600">
            Our AI detected potential goals in your entry. Select the ones you'd like to add:
          </p>
          
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {detectedGoals.map((goal, index) => (
              <div
                key={index}
                className={`border rounded-lg p-4 cursor-pointer transition-all ${
                  selectedGoals.includes(index)
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                onClick={() => handleGoalToggle(index)}
              >
                <div className="flex items-start space-x-3">
                  <div className={`w-5 h-5 rounded border-2 flex items-center justify-center mt-0.5 ${
                    selectedGoals.includes(index)
                      ? 'border-blue-500 bg-blue-500'
                      : 'border-gray-300'
                  }`}>
                    {selectedGoals.includes(index) && (
                      <Check className="w-3 h-3 text-white" />
                    )}
                  </div>
                  
                  <div className="flex-1">
                    <p className="font-medium text-gray-800 mb-2">
                      {goal.goal_statement}
                    </p>
                    
                    <div className="flex items-center space-x-2">
                      <span className="text-xs text-gray-500">AI Confidence:</span>
                      <span className={`text-xs px-2 py-1 rounded-full ${getConfidenceColor(goal.confidence)}`}>
                        {getConfidenceLabel(goal.confidence)} ({Math.round(goal.confidence * 100)}%)
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
          
          {detectedGoals.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              <Target className="w-12 h-12 mx-auto mb-3 text-gray-300" />
              <p>No goals were detected in this entry.</p>
            </div>
          )}
          
          <div className="flex justify-between items-center pt-4 border-t">
            <div className="text-sm text-gray-600">
              {selectedGoals.length} of {detectedGoals.length} goals selected
            </div>
            
            <div className="flex space-x-3">
              <Button
                onClick={onClose}
                variant="outline"
              >
                Skip for Now
              </Button>
              <Button
                onClick={handleAcceptGoals}
                disabled={isAccepting}
              >
                {isAccepting ? (
                  <div className="flex items-center space-x-2">
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    <span>Adding...</span>
                  </div>
                ) : selectedGoals.length > 0 ? (
                  `Add ${selectedGoals.length} Goal${selectedGoals.length > 1 ? 's' : ''}`
                ) : (
                  'Continue'
                )}
              </Button>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}