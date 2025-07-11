"use client";

import { useState } from 'react';
import { Lock, Check, AlertTriangle } from 'lucide-react';
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

interface FreemiumEntryGateProps {
  freemiumStatus: FreemiumStatus;
  onClose: () => void;
}

export function FreemiumEntryGate({ freemiumStatus, onClose }: FreemiumEntryGateProps) {
  const [isRequestingCoach, setIsRequestingCoach] = useState(false);
  const [requestForm, setRequestForm] = useState({
    message: '',
    preferred_contact: 'email' as 'email' | 'phone',
    contact_info: ''
  });

  const handleRequestCoach = async () => {
    setIsRequestingCoach(true);
    try {
      const response = await fetch('/api/v1/coach-request', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: requestForm.message || 'I would like to connect with a coach to unlock unlimited entries.',
          preferred_contact: requestForm.preferred_contact,
          contact_info: requestForm.contact_info
        })
      });

      if (response.ok) {
        // Show success message (you might want to use a toast library)
        alert('Coach request submitted! We\'ll be in touch soon.');
        onClose();
      } else {
        throw new Error('Failed to submit request');
      }
    } catch (error) {
      console.error('Error requesting coach:', error);
      alert('Failed to submit coach request. Please try again.');
    } finally {
      setIsRequestingCoach(false);
    }
  };

  return (
    <div className="p-8">
      <div className="text-center mb-6">
        <div className="w-16 h-16 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <Lock className="w-8 h-8 text-orange-500" />
        </div>
        
        <h3 className="text-xl font-semibold text-gray-800 mb-2">
          Entry Limit Reached
        </h3>
        
        <p className="text-gray-600">
          You've used all {freemiumStatus.max_free_entries} of your free entries. 
          Connect with a coach to unlock unlimited entries and advanced features.
        </p>
      </div>
      
      <div className="space-y-6">
        <div className="bg-blue-50 rounded-lg p-4">
          <h4 className="font-medium text-blue-800 mb-3">With a coach, you get:</h4>
          <ul className="text-sm text-blue-700 space-y-2">
            <li className="flex items-center space-x-2">
              <Check className="w-4 h-4 text-blue-600" />
              <span>Unlimited entry creation</span>
            </li>
            <li className="flex items-center space-x-2">
              <Check className="w-4 h-4 text-blue-600" />
              <span>Advanced AI insights and analysis</span>
            </li>
            <li className="flex items-center space-x-2">
              <Check className="w-4 h-4 text-blue-600" />
              <span>Personalized coaching resources</span>
            </li>
            <li className="flex items-center space-x-2">
              <Check className="w-4 h-4 text-blue-600" />
              <span>Goal tracking and progress monitoring</span>
            </li>
            <li className="flex items-center space-x-2">
              <Check className="w-4 h-4 text-blue-600" />
              <span>Direct coach communication</span>
            </li>
          </ul>
        </div>
        
        {/* Coach Request Form */}
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Tell us about your coaching needs (optional)
            </label>
            <textarea
              value={requestForm.message}
              onChange={(e) => setRequestForm(prev => ({ ...prev, message: e.target.value }))}
              placeholder="What are you hoping to achieve with coaching?"
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              rows={3}
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Preferred contact method
            </label>
            <select
              value={requestForm.preferred_contact}
              onChange={(e) => setRequestForm(prev => ({ 
                ...prev, 
                preferred_contact: e.target.value as 'email' | 'phone' 
              }))}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="email">Email</option>
              <option value="phone">Phone</option>
            </select>
          </div>
        </div>
        
        <div className="flex space-x-3">
          <Button
            onClick={onClose}
            variant="outline"
            className="flex-1"
          >
            Maybe Later
          </Button>
          <Button
            onClick={handleRequestCoach}
            disabled={isRequestingCoach}
            className="flex-1"
          >
            {isRequestingCoach ? 'Requesting...' : 'Request Coach'}
          </Button>
        </div>
      </div>
    </div>
  );
}