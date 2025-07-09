'use client';

import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { 
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { 
  Share2, 
  Loader2, 
  CheckCircle,
  AlertCircle,
  Users
} from 'lucide-react';
import { sessionInsightService, SessionInsight, ShareInsightRequest } from '@/services/sessionInsightService';
import { useAuth } from '@/context/AuthContext';
import { useToast } from '@/hooks/use-toast';

interface InsightSharingModalProps {
  insight: SessionInsight | null;
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

// Mock coaches data - in a real app, this would come from an API
const mockCoaches = [
  { id: 'coach1', name: 'Dr. Sarah Johnson', email: 'sarah.johnson@example.com' },
  { id: 'coach2', name: 'Michael Chen', email: 'michael.chen@example.com' },
  { id: 'coach3', name: 'Emily Rodriguez', email: 'emily.rodriguez@example.com' },
];

export function InsightSharingModal({ insight, isOpen, onClose, onSuccess }: InsightSharingModalProps) {
  const { getAuthToken } = useAuth();
  const { toast } = useToast();
  
  const [selectedCoach, setSelectedCoach] = useState<string>('');
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Reset form when modal opens/closes
  useEffect(() => {
    if (isOpen) {
      setSelectedCoach('');
      setMessage('');
      setError(null);
    }
  }, [isOpen]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!insight || !selectedCoach) {
      setError('Please select a coach to share with');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      const token = await getAuthToken();
      if (!token) {
        throw new Error("Authentication token not available");
      }

      const selectedCoachData = mockCoaches.find(coach => coach.id === selectedCoach);
      if (!selectedCoachData) {
        throw new Error("Selected coach not found");
      }

      const shareData: ShareInsightRequest = {
        coach_email: selectedCoachData.email,
        message: message.trim() || undefined,
      };

      await sessionInsightService.shareInsight(token, insight.id, shareData);
      
      toast({
        title: "Insight Shared!",
        description: `Your insight has been shared with ${selectedCoachData.name}.`,
      });

      onSuccess?.();
      onClose();
    } catch (err) {
      console.error('Error sharing insight:', err);
      const errorMessage = err instanceof Error ? err.message : 'Failed to share insight. Please try again.';
      setError(errorMessage);
      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  if (!insight) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Share2 className="h-5 w-5 text-blue-600" />
            </div>
            <div>
              <DialogTitle>Share Insight</DialogTitle>
              <DialogDescription>
                Share "{insight.session_title || insight.title || 'Untitled Insight'}" with a coach
              </DialogDescription>
            </div>
          </div>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-md text-red-700">
              <AlertCircle className="h-4 w-4" />
              <span className="text-sm">{error}</span>
            </div>
          )}

          <div className="space-y-2">
            <Label htmlFor="coach">Select Coach *</Label>
            <Select value={selectedCoach} onValueChange={setSelectedCoach} disabled={loading}>
              <SelectTrigger>
                <SelectValue placeholder="Choose a coach to share with..." />
              </SelectTrigger>
              <SelectContent>
                {mockCoaches.map((coach) => (
                  <SelectItem key={coach.id} value={coach.id}>
                    <div className="flex items-center gap-2">
                      <Users className="h-4 w-4" />
                      <div>
                        <div className="font-medium">{coach.name}</div>
                        <div className="text-xs text-gray-500">{coach.email}</div>
                      </div>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="message">Message (Optional)</Label>
            <Textarea
              id="message"
              placeholder="Add a personal message to accompany your insight..."
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              disabled={loading}
              rows={3}
              className="resize-none"
            />
          </div>

          <div className="flex gap-3 pt-2">
            <Button
              type="submit"
              disabled={loading || !selectedCoach}
              className="flex-1"
            >
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Sharing...
                </>
              ) : (
                <>
                  <Share2 className="mr-2 h-4 w-4" />
                  Share Insight
                </>
              )}
            </Button>
            
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              disabled={loading}
            >
              Cancel
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}