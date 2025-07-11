'use client';

import { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { UserPlus, Send, X, Heart } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';

interface CoachRequestModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  context: 'entry_limit' | 'feature_lock' | 'insights_limit' | 'destinations_limit';
}

interface RequestFormData {
  goals: string;
  experience_level: string;
  preferred_coaching_style: string;
  availability: string;
  specific_challenges: string;
  motivation: string;
  terms_accepted: boolean;
}

export function CoachRequestModal({ isOpen, onClose, onSuccess, context }: CoachRequestModalProps) {
  const { user, getAuthToken } = useAuth();
  const [formData, setFormData] = useState<RequestFormData>({
    goals: '',
    experience_level: 'beginner',
    preferred_coaching_style: 'supportive',
    availability: 'flexible',
    specific_challenges: '',
    motivation: '',
    terms_accepted: false
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const contextMessages = {
    entry_limit: 'You\'ve reached your free entry limit and want to continue your growth journey.',
    feature_lock: 'You\'re interested in accessing premium features to enhance your experience.',
    insights_limit: 'You want deeper AI insights and analysis for your personal development.',
    destinations_limit: 'You\'re ready to set and achieve more ambitious goals with coaching support.'
  };

  const experienceLevels = [
    { value: 'beginner', label: 'New to personal development' },
    { value: 'intermediate', label: 'Some experience with self-improvement' },
    { value: 'advanced', label: 'Experienced in personal growth work' },
    { value: 'expert', label: 'Highly experienced, seeking advanced guidance' }
  ];

  const coachingStyles = [
    { value: 'supportive', label: 'Supportive and encouraging' },
    { value: 'challenging', label: 'Direct and challenging' },
    { value: 'analytical', label: 'Data-driven and analytical' },
    { value: 'holistic', label: 'Holistic and mindful' },
    { value: 'goal_oriented', label: 'Goal-oriented and structured' }
  ];

  const availabilityOptions = [
    { value: 'flexible', label: 'Flexible scheduling' },
    { value: 'weekdays', label: 'Weekdays only' },
    { value: 'weekends', label: 'Weekends only' },
    { value: 'evenings', label: 'Evenings only' },
    { value: 'mornings', label: 'Mornings only' }
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.goals.trim()) {
      setError('Please describe your goals');
      return;
    }

    if (!formData.terms_accepted) {
      setError('Please accept the terms and conditions');
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
      const response = await fetch(`${apiUrl}/api/v1/freemium/request-coach`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          context,
          context_message: contextMessages[context],
          goals: formData.goals.trim(),
          experience_level: formData.experience_level,
          preferred_coaching_style: formData.preferred_coaching_style,
          availability: formData.availability,
          specific_challenges: formData.specific_challenges.trim(),
          motivation: formData.motivation.trim(),
          user_info: {
            name: `${user?.firstName} ${user?.lastName}`.trim(),
            email: user?.email
          }
        })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to submit coach request');
      }

      onSuccess();
    } catch (error) {
      console.error('Error submitting coach request:', error);
      setError(error instanceof Error ? error.message : 'Failed to submit request');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    if (!isSubmitting) {
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <UserPlus className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <DialogTitle className="text-xl">Request Coach Access</DialogTitle>
                <DialogDescription>
                  Tell us about your goals and we'll match you with the right coach
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

        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-600">{error}</p>
            </div>
          )}

          {/* Context Message */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <p className="text-sm text-blue-800">
              <strong>Why you're here:</strong> {contextMessages[context]}
            </p>
          </div>

          {/* Goals */}
          <div className="space-y-2">
            <Label htmlFor="goals">What are your main goals? *</Label>
            <Textarea
              id="goals"
              value={formData.goals}
              onChange={(e) => setFormData(prev => ({ ...prev, goals: e.target.value }))}
              placeholder="Describe what you want to achieve through coaching..."
              disabled={isSubmitting}
              className="min-h-[100px]"
              maxLength={1000}
            />
            <p className="text-xs text-gray-500">{formData.goals.length}/1000 characters</p>
          </div>

          {/* Experience Level */}
          <div className="space-y-2">
            <Label htmlFor="experience_level">Experience Level</Label>
            <Select
              value={formData.experience_level}
              onValueChange={(value) => setFormData(prev => ({ ...prev, experience_level: value }))}
              disabled={isSubmitting}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {experienceLevels.map((level) => (
                  <SelectItem key={level.value} value={level.value}>
                    {level.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Coaching Style */}
          <div className="space-y-2">
            <Label htmlFor="coaching_style">Preferred Coaching Style</Label>
            <Select
              value={formData.preferred_coaching_style}
              onValueChange={(value) => setFormData(prev => ({ ...prev, preferred_coaching_style: value }))}
              disabled={isSubmitting}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {coachingStyles.map((style) => (
                  <SelectItem key={style.value} value={style.value}>
                    {style.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Availability */}
          <div className="space-y-2">
            <Label htmlFor="availability">Availability</Label>
            <Select
              value={formData.availability}
              onValueChange={(value) => setFormData(prev => ({ ...prev, availability: value }))}
              disabled={isSubmitting}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {availabilityOptions.map((option) => (
                  <SelectItem key={option.value} value={option.value}>
                    {option.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Specific Challenges */}
          <div className="space-y-2">
            <Label htmlFor="challenges">Specific Challenges (Optional)</Label>
            <Textarea
              id="challenges"
              value={formData.specific_challenges}
              onChange={(e) => setFormData(prev => ({ ...prev, specific_challenges: e.target.value }))}
              placeholder="Any specific challenges or areas you'd like to focus on..."
              disabled={isSubmitting}
              className="min-h-[80px]"
              maxLength={500}
            />
            <p className="text-xs text-gray-500">{formData.specific_challenges.length}/500 characters</p>
          </div>

          {/* Motivation */}
          <div className="space-y-2">
            <Label htmlFor="motivation">What motivates you? (Optional)</Label>
            <Textarea
              id="motivation"
              value={formData.motivation}
              onChange={(e) => setFormData(prev => ({ ...prev, motivation: e.target.value }))}
              placeholder="What drives you to seek coaching and personal growth..."
              disabled={isSubmitting}
              className="min-h-[80px]"
              maxLength={500}
            />
            <p className="text-xs text-gray-500">{formData.motivation.length}/500 characters</p>
          </div>

          {/* Terms and Conditions */}
          <div className="flex items-start space-x-2">
            <Checkbox
              id="terms"
              checked={formData.terms_accepted}
              onCheckedChange={(checked: boolean) => setFormData(prev => ({ ...prev, terms_accepted: checked }))}
              disabled={isSubmitting}
            />
            <Label htmlFor="terms" className="text-sm leading-relaxed">
              I agree to the terms and conditions and understand that coach matching may take 1-3 business days. 
              I consent to being contacted by a coach via email or the platform.
            </Label>
          </div>

          {/* What Happens Next */}
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <h4 className="text-sm font-medium text-green-800 mb-2 flex items-center">
              <Heart className="w-4 h-4 mr-2" />
              What happens next?
            </h4>
            <ul className="text-xs text-green-700 space-y-1">
              <li>• We'll review your request within 1-3 business days</li>
              <li>• You'll be matched with a coach based on your preferences</li>
              <li>• Your coach will reach out to schedule an initial session</li>
              <li>• You'll gain access to all premium features immediately</li>
            </ul>
          </div>

          <div className="flex gap-3 pt-4">
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
              disabled={isSubmitting || !formData.goals.trim() || !formData.terms_accepted}
              className="flex-1 bg-blue-600 text-white hover:bg-blue-700"
            >
              {isSubmitting ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                  Submitting...
                </>
              ) : (
                <>
                  <Send className="w-4 h-4 mr-2" />
                  Submit Request
                </>
              )}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}