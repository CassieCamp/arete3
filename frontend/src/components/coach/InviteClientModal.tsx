'use client';

import { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Mail, Send, X } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';

interface InviteClientModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export function InviteClientModal({ isOpen, onClose, onSuccess }: InviteClientModalProps) {
  const { getAuthToken } = useAuth();
  const [formData, setFormData] = useState({
    email: '',
    personalMessage: ''
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.email.trim()) {
      setError('Email is required');
      return;
    }

    if (!isValidEmail(formData.email)) {
      setError('Please enter a valid email address');
      return;
    }

    try {
      setIsSubmitting(true);
      setError(null);

      const token = await getAuthToken();
      if (!token) {
        throw new Error('No authentication token available');
      }

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/v1/coaching-relationships/invite`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          client_email: formData.email.trim(),
          personal_message: formData.personalMessage.trim() || undefined
        })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to send invitation');
      }

      // Reset form and close modal
      setFormData({ email: '', personalMessage: '' });
      onSuccess();
      onClose();
    } catch (error) {
      console.error('Error sending invitation:', error);
      setError(error instanceof Error ? error.message : 'Failed to send invitation');
    } finally {
      setIsSubmitting(false);
    }
  };

  const isValidEmail = (email: string) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  const handleClose = () => {
    if (!isSubmitting) {
      setFormData({ email: '', personalMessage: '' });
      setError(null);
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Mail className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <DialogTitle>Invite Client</DialogTitle>
                <DialogDescription>
                  Send a coaching invitation to a new client
                </DialogDescription>
              </div>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleClose}
              disabled={isSubmitting}
              className="h-8 w-8 p-0"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-600">{error}</p>
            </div>
          )}

          <div className="space-y-2">
            <Label htmlFor="email">Client Email Address *</Label>
            <Input
              id="email"
              type="email"
              value={formData.email}
              onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
              placeholder="client@example.com"
              disabled={isSubmitting}
              className="w-full"
            />
            <p className="text-xs text-gray-500">
              The client will receive an invitation email to join your coaching relationship.
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="personalMessage">Personal Message (Optional)</Label>
            <Textarea
              id="personalMessage"
              value={formData.personalMessage}
              onChange={(e) => setFormData(prev => ({ ...prev, personalMessage: e.target.value }))}
              placeholder="Add a personal note to your invitation..."
              disabled={isSubmitting}
              className="min-h-[80px] resize-none"
              maxLength={500}
            />
            <p className="text-xs text-gray-500">
              {formData.personalMessage.length}/500 characters
            </p>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
            <h4 className="text-sm font-medium text-blue-800 mb-1">What happens next?</h4>
            <ul className="text-xs text-blue-700 space-y-1">
              <li>• The client will receive an invitation email</li>
              <li>• They can accept or decline the coaching relationship</li>
              <li>• You'll be notified of their response</li>
              <li>• Once accepted, you can start coaching together</li>
            </ul>
          </div>

          <div className="flex gap-3 pt-2">
            <Button
              type="button"
              variant="outline"
              onClick={handleClose}
              disabled={isSubmitting}
              className="flex-1"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={isSubmitting || !formData.email.trim()}
              className="flex-1 bg-blue-600 text-white hover:bg-blue-700"
            >
              {isSubmitting ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                  Sending...
                </>
              ) : (
                <>
                  <Send className="w-4 h-4 mr-2" />
                  Send Invitation
                </>
              )}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}