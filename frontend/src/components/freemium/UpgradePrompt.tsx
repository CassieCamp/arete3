'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Sparkles, Check, Crown, ArrowRight } from 'lucide-react';
import { CoachRequestModal } from './CoachRequestModal';

interface FreemiumStatus {
  has_coach: boolean;
  entries_count: number;
  max_free_entries: number;
  entries_remaining: number;
  can_create_entries: boolean;
  can_access_insights: boolean;
  can_access_destinations: boolean;
  is_freemium: boolean;
  coach_requested: boolean;
  coach_request_date: string | null;
}

interface UpgradePromptProps {
  context: 'entry_limit' | 'feature_lock' | 'insights_limit' | 'destinations_limit';
  freemiumStatus: FreemiumStatus;
  onUpgradeRequest?: () => void;
}

export function UpgradePrompt({ context, freemiumStatus, onUpgradeRequest }: UpgradePromptProps) {
  const [showRequestModal, setShowRequestModal] = useState(false);

  const prompts = {
    entry_limit: {
      title: 'Unlock Unlimited Entries',
      description: 'You\'ve reached your free entry limit. Connect with a coach to continue your journey.',
      icon: Sparkles,
      iconColor: 'text-blue-600',
      bgColor: 'from-blue-50 to-indigo-50',
      borderColor: 'border-blue-200',
      benefits: [
        'Unlimited session and thought entries',
        'Advanced AI insights and analysis',
        'Goal tracking and progress monitoring',
        'Personalized coaching resources'
      ]
    },
    feature_lock: {
      title: 'Premium Feature',
      description: 'This feature is available with coach access. Unlock your full potential.',
      icon: Crown,
      iconColor: 'text-purple-600',
      bgColor: 'from-purple-50 to-pink-50',
      borderColor: 'border-purple-200',
      benefits: [
        'Access to all premium features',
        'Personalized coaching guidance',
        'Advanced analytics and insights',
        'Priority support'
      ]
    },
    insights_limit: {
      title: 'Deeper Insights Available',
      description: 'Get more detailed AI analysis and coaching insights with a coach.',
      icon: Sparkles,
      iconColor: 'text-green-600',
      bgColor: 'from-green-50 to-emerald-50',
      borderColor: 'border-green-200',
      benefits: [
        'Comprehensive AI analysis',
        'Coaching-specific insights',
        'Progress tracking over time',
        'Personalized recommendations'
      ]
    },
    destinations_limit: {
      title: 'Enhanced Goal Setting',
      description: 'Unlock advanced destination features with personalized coaching support.',
      icon: Crown,
      iconColor: 'text-orange-600',
      bgColor: 'from-orange-50 to-yellow-50',
      borderColor: 'border-orange-200',
      benefits: [
        'Unlimited destination creation',
        'Coach-guided goal setting',
        'Progress tracking and milestones',
        'Accountability partnerships'
      ]
    }
  };

  const prompt = prompts[context];
  const IconComponent = prompt.icon;

  const handleRequestCoach = () => {
    setShowRequestModal(true);
  };

  const handleRequestSuccess = () => {
    setShowRequestModal(false);
    onUpgradeRequest?.();
  };

  // If user has already requested a coach, show different content
  if (freemiumStatus.coach_requested) {
    return (
      <Card className={`bg-gradient-to-r ${prompt.bgColor} border ${prompt.borderColor}`}>
        <CardContent className="p-6">
          <div className="flex items-start space-x-4">
            <div className="p-2 bg-white rounded-lg shadow-sm">
              <Check className="w-6 h-6 text-green-600" />
            </div>
            
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-gray-800 mb-2">
                Coach Request Submitted
              </h3>
              <p className="text-gray-600 mb-4">
                We've received your request for coaching access. Our team will review your application and get back to you soon.
              </p>
              
              <div className="bg-white/50 rounded-lg p-3 mb-4">
                <p className="text-sm text-gray-700">
                  <strong>What's next?</strong> You'll receive an email notification once a coach is assigned to you. 
                  In the meantime, you can continue using your remaining free entries.
                </p>
              </div>

              <div className="flex items-center text-sm text-gray-600">
                <span>Requested on {new Date(freemiumStatus.coach_request_date!).toLocaleDateString()}</span>
                <Badge variant="secondary" className="ml-2">Pending Review</Badge>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <>
      <Card className={`bg-gradient-to-r ${prompt.bgColor} border ${prompt.borderColor}`}>
        <CardContent className="p-6">
          <div className="flex items-start space-x-4">
            <div className="p-2 bg-white rounded-lg shadow-sm">
              <IconComponent className={`w-6 h-6 ${prompt.iconColor}`} />
            </div>
            
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-gray-800 mb-2">
                {prompt.title}
              </h3>
              <p className="text-gray-600 mb-4">
                {prompt.description}
              </p>
              
              <div className="mb-4">
                <h4 className="font-medium text-gray-800 mb-2">What you'll get:</h4>
                <ul className="space-y-1">
                  {prompt.benefits.map((benefit, index) => (
                    <li key={index} className="flex items-center text-sm text-gray-700">
                      <Check className="w-4 h-4 text-green-500 mr-2 flex-shrink-0" />
                      {benefit}
                    </li>
                  ))}
                </ul>
              </div>
              
              <div className="flex space-x-3">
                <Button
                  onClick={handleRequestCoach}
                  className={`${prompt.iconColor.replace('text-', 'bg-').replace('-600', '-600')} text-white hover:opacity-90`}
                >
                  Request Coach Access
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
                <Button variant="outline" size="sm" className="text-gray-600">
                  Learn More
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <CoachRequestModal
        isOpen={showRequestModal}
        onClose={() => setShowRequestModal(false)}
        onSuccess={handleRequestSuccess}
        context={context}
      />
    </>
  );
}