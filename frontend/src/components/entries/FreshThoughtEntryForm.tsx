"use client";

import { useState, useEffect } from 'react';
import { AlertTriangle } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface FreemiumStatus {
  has_coach: boolean;
  entries_count: number;
  max_free_entries: number;
  entries_remaining: number;
  can_create_entries: boolean;
  can_access_insights: boolean;
  is_freemium: boolean;
}

interface EntryFormData {
  content: string;
  session_date: string;
  input_method: 'paste';
  title?: string;
}

interface FreshThoughtEntryFormProps {
  onSubmit: (data: EntryFormData) => Promise<void>;
  isSubmitting: boolean;
  freemiumStatus: FreemiumStatus;
}

export function FreshThoughtEntryForm({ onSubmit, isSubmitting, freemiumStatus }: FreshThoughtEntryFormProps) {
  const [formData, setFormData] = useState<EntryFormData>({
    content: '',
    session_date: new Date().toISOString().split('T')[0],
    input_method: 'paste',
    title: ''
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [wordCount, setWordCount] = useState(0);

  useEffect(() => {
    const words = formData.content.trim().split(/\s+/).filter(word => word.length > 0);
    setWordCount(words.length);
  }, [formData.content]);

  const validateForm = () => {
    const newErrors: Record<string, string> = {};
    
    if (!formData.content.trim()) {
      newErrors.content = 'Please share your thoughts';
    } else if (formData.content.trim().length < 10) {
      newErrors.content = 'Please write at least 10 characters';
    }
    
    if (!formData.session_date) {
      newErrors.session_date = 'Date is required';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) return;
    
    await onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Content Input */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          What's on your mind? *
        </label>
        <textarea
          value={formData.content}
          onChange={(e) => setFormData(prev => ({ ...prev, content: e.target.value }))}
          placeholder="Share your thoughts, insights, reflections, or anything that's on your mind..."
          className={`w-full h-40 p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none ${
            errors.content ? 'border-red-500' : 'border-gray-300'
          }`}
          required
        />
        <div className="flex justify-between items-center mt-1">
          <div className="text-xs text-gray-500">
            {formData.content.length} characters • {wordCount} words
          </div>
          {errors.content && (
            <div className="text-xs text-red-500">{errors.content}</div>
          )}
        </div>
      </div>
      
      {/* Date */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Date *
        </label>
        <input
          type="date"
          value={formData.session_date}
          onChange={(e) => setFormData(prev => ({ ...prev, session_date: e.target.value }))}
          max={new Date().toISOString().split('T')[0]}
          className={`w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
            errors.session_date ? 'border-red-500' : 'border-gray-300'
          }`}
          required
        />
        {errors.session_date && (
          <div className="mt-1 text-xs text-red-500">{errors.session_date}</div>
        )}
      </div>
      
      {/* Optional Title */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Title (Optional)
        </label>
        <input
          type="text"
          value={formData.title}
          onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
          placeholder="AI will generate a title if left blank"
          maxLength={100}
          className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
        <div className="mt-1 text-xs text-gray-500">
          {formData.title ? `${formData.title.length}/100 characters` : 'Leave blank for AI-generated title'}
        </div>
      </div>
      
      {/* Freemium Warning */}
      {!freemiumStatus.has_coach && (
        <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
          <div className="flex items-start space-x-3">
            <AlertTriangle className="w-5 h-5 text-orange-500 mt-0.5 flex-shrink-0" />
            <div>
              <div className="font-medium text-orange-800">
                {freemiumStatus.entries_remaining} free entries remaining
              </div>
              <div className="text-sm text-orange-700 mt-1">
                Connect with a coach for unlimited entries and advanced features.
              </div>
            </div>
          </div>
        </div>
      )}
      
      {/* Submit Button */}
      <div className="flex space-x-3">
        <Button
          type="submit"
          disabled={!formData.content.trim() || isSubmitting}
          className="flex-1"
        >
          {isSubmitting ? (
            <div className="flex items-center justify-center space-x-2">
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              <span>Processing...</span>
            </div>
          ) : (
            'Add Thought'
          )}
        </Button>
      </div>
    </form>
  );
}