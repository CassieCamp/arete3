"use client";

import { useState, useEffect } from 'react';
import { useAuth } from '@/context/AuthContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { CheckCircle, Circle, ArrowRight, ArrowLeft, X } from 'lucide-react';

interface OnboardingStep {
  id: number;
  title: string;
  description: string;
  component: React.ComponentType<OnboardingStepProps>;
  required: boolean;
}

interface OnboardingStepProps {
  onNext: () => void;
  onSkip?: () => void;
  userRole: 'coach' | 'client';
}

interface OnboardingState {
  completed: boolean;
  current_step: number;
  steps_completed: number[];
  started_at: string | null;
  completed_at: string | null;
}

// Step Components
function WelcomeStep({ onNext, userRole }: OnboardingStepProps) {
  return (
    <div className="text-center space-y-6">
      <div className="space-y-2">
        <h2 className="text-2xl font-bold">Welcome to Arete!</h2>
        <p className="text-muted-foreground">
          {userRole === 'coach' 
            ? "Let's get you set up to start coaching and managing your clients effectively."
            : "Let's get you started on your coaching journey and help you achieve your goals."
          }
        </p>
      </div>
      
      <div className="bg-blue-50 p-4 rounded-lg">
        <p className="text-sm text-blue-800">
          This quick setup will take about 3-5 minutes and will help you get the most out of Arete.
        </p>
      </div>
      
      <Button onClick={onNext} className="w-full">
        Get Started <ArrowRight className="ml-2 h-4 w-4" />
      </Button>
    </div>
  );
}

function ProfileSetupStep({ onNext, onSkip, userRole }: OnboardingStepProps) {
  const [hasProfile, setHasProfile] = useState(false);
  const [loading, setLoading] = useState(true);
  const { getAuthToken } = useAuth();

  useEffect(() => {
    checkProfile();
  }, []);

  const checkProfile = async () => {
    try {
      const token = await getAuthToken();
      const response = await fetch('http://localhost:8000/api/v1/users/me/profile', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      
      setHasProfile(response.ok);
    } catch (error) {
      console.error('Error checking profile:', error);
      setHasProfile(false);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateProfile = () => {
    window.location.href = userRole === 'coach' 
      ? '/profile/create/coach' 
      : '/profile/create/client';
  };

  if (loading) {
    return (
      <div className="text-center space-y-4">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
        <p>Checking your profile...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="text-center space-y-2">
        <h2 className="text-xl font-semibold">Complete Your Profile</h2>
        <p className="text-muted-foreground">
          {hasProfile 
            ? "Great! Your profile is already set up."
            : `Set up your ${userRole} profile to get personalized recommendations and connect with others.`
          }
        </p>
      </div>

      {hasProfile ? (
        <div className="bg-green-50 p-4 rounded-lg text-center">
          <CheckCircle className="h-8 w-8 text-green-600 mx-auto mb-2" />
          <p className="text-green-800 font-medium">Profile Complete!</p>
          <p className="text-green-700 text-sm">You can always update your profile later in settings.</p>
        </div>
      ) : (
        <div className="bg-yellow-50 p-4 rounded-lg text-center">
          <Circle className="h-8 w-8 text-yellow-600 mx-auto mb-2" />
          <p className="text-yellow-800 font-medium">Profile Setup Required</p>
          <p className="text-yellow-700 text-sm mb-4">
            Complete your profile to unlock all features and get better recommendations.
          </p>
          <Button onClick={handleCreateProfile} className="w-full">
            Create Profile
          </Button>
        </div>
      )}

      <div className="flex gap-2">
        {hasProfile ? (
          <Button onClick={onNext} className="flex-1">
            Continue <ArrowRight className="ml-2 h-4 w-4" />
          </Button>
        ) : (
          <>
            <Button variant="outline" onClick={onSkip} className="flex-1">
              Skip for Now
            </Button>
            <Button onClick={handleCreateProfile} className="flex-1">
              Create Profile
            </Button>
          </>
        )}
      </div>
    </div>
  );
}

function DashboardTourStep({ onNext, userRole }: OnboardingStepProps) {
  return (
    <div className="space-y-6">
      <div className="text-center space-y-2">
        <h2 className="text-xl font-semibold">Explore Your Dashboard</h2>
        <p className="text-muted-foreground">
          Your dashboard is your command center. Here's what you'll find:
        </p>
      </div>

      <div className="space-y-4">
        {userRole === 'coach' ? (
          <>
            <div className="flex items-start space-x-3 p-3 bg-blue-50 rounded-lg">
              <div className="w-2 h-2 bg-blue-600 rounded-full mt-2"></div>
              <div>
                <h3 className="font-medium">Client Management</h3>
                <p className="text-sm text-muted-foreground">View and manage your coaching relationships</p>
              </div>
            </div>
            <div className="flex items-start space-x-3 p-3 bg-blue-50 rounded-lg">
              <div className="w-2 h-2 bg-blue-600 rounded-full mt-2"></div>
              <div>
                <h3 className="font-medium">Session Insights</h3>
                <p className="text-sm text-muted-foreground">Generate AI-powered insights from coaching sessions</p>
              </div>
            </div>
            <div className="flex items-start space-x-3 p-3 bg-blue-50 rounded-lg">
              <div className="w-2 h-2 bg-blue-600 rounded-full mt-2"></div>
              <div>
                <h3 className="font-medium">Progress Tracking</h3>
                <p className="text-sm text-muted-foreground">Monitor client progress and goal achievement</p>
              </div>
            </div>
          </>
        ) : (
          <>
            <div className="flex items-start space-x-3 p-3 bg-blue-50 rounded-lg">
              <div className="w-2 h-2 bg-blue-600 rounded-full mt-2"></div>
              <div>
                <h3 className="font-medium">Goal Setting</h3>
                <p className="text-sm text-muted-foreground">Create and track your personal development goals</p>
              </div>
            </div>
            <div className="flex items-start space-x-3 p-3 bg-blue-50 rounded-lg">
              <div className="w-2 h-2 bg-blue-600 rounded-full mt-2"></div>
              <div>
                <h3 className="font-medium">Session Insights</h3>
                <p className="text-sm text-muted-foreground">Review insights from your coaching sessions</p>
              </div>
            </div>
            <div className="flex items-start space-x-3 p-3 bg-blue-50 rounded-lg">
              <div className="w-2 h-2 bg-blue-600 rounded-full mt-2"></div>
              <div>
                <h3 className="font-medium">Progress Overview</h3>
                <p className="text-sm text-muted-foreground">See your growth and achievements over time</p>
              </div>
            </div>
          </>
        )}
      </div>

      <Button onClick={onNext} className="w-full">
        Explore Dashboard <ArrowRight className="ml-2 h-4 w-4" />
      </Button>
    </div>
  );
}

function FirstActionStep({ onNext, userRole }: OnboardingStepProps) {
  const handleAction = (path: string) => {
    window.location.href = path;
  };

  return (
    <div className="space-y-6">
      <div className="text-center space-y-2">
        <h2 className="text-xl font-semibold">Take Your First Action</h2>
        <p className="text-muted-foreground">
          {userRole === 'coach' 
            ? "Start by connecting with your first client or generating insights."
            : "Begin your journey by setting a goal or exploring your coaching relationship."
          }
        </p>
      </div>

      <div className="grid gap-3">
        {userRole === 'coach' ? (
          <>
            <Button 
              variant="outline" 
              className="h-auto p-4 text-left"
              onClick={() => handleAction('/dashboard/connections')}
            >
              <div>
                <h3 className="font-medium">View Client Connections</h3>
                <p className="text-sm text-muted-foreground">Manage your coaching relationships</p>
              </div>
            </Button>
            <Button 
              variant="outline" 
              className="h-auto p-4 text-left"
              onClick={() => handleAction('/dashboard/insights')}
            >
              <div>
                <h3 className="font-medium">Generate Session Insight</h3>
                <p className="text-sm text-muted-foreground">Create your first AI-powered insight</p>
              </div>
            </Button>
          </>
        ) : (
          <>
            <Button 
              variant="outline" 
              className="h-auto p-4 text-left"
              onClick={() => handleAction('/dashboard/goals')}
            >
              <div>
                <h3 className="font-medium">Set Your First Goal</h3>
                <p className="text-sm text-muted-foreground">Define what you want to achieve</p>
              </div>
            </Button>
            <Button 
              variant="outline" 
              className="h-auto p-4 text-left"
              onClick={() => handleAction('/dashboard/connections')}
            >
              <div>
                <h3 className="font-medium">View Coaching Relationship</h3>
                <p className="text-sm text-muted-foreground">Connect with your coach</p>
              </div>
            </Button>
          </>
        )}
      </div>

      <Button onClick={onNext} variant="ghost" className="w-full">
        I'll do this later <ArrowRight className="ml-2 h-4 w-4" />
      </Button>
    </div>
  );
}

function CompletionStep({ onNext, userRole }: OnboardingStepProps) {
  return (
    <div className="text-center space-y-6">
      <div className="space-y-2">
        <CheckCircle className="h-16 w-16 text-green-600 mx-auto" />
        <h2 className="text-2xl font-bold">You're All Set!</h2>
        <p className="text-muted-foreground">
          {userRole === 'coach' 
            ? "Welcome to Arete! You're ready to start coaching with AI-enhanced insights."
            : "Welcome to Arete! You're ready to begin your coaching journey."
          }
        </p>
      </div>
      
      <div className="bg-green-50 p-4 rounded-lg">
        <p className="text-sm text-green-800">
          You can always access help and tutorials from the dashboard menu.
        </p>
      </div>
      
      <Button onClick={onNext} className="w-full">
        Go to Dashboard
      </Button>
    </div>
  );
}

export function OnboardingGuide() {
  const { user, getAuthToken } = useAuth();
  const [currentStep, setCurrentStep] = useState(0);
  const [onboardingState, setOnboardingState] = useState<OnboardingState | null>(null);
  const [loading, setLoading] = useState(true);
  const [isVisible, setIsVisible] = useState(false);

  const userRole = (user?.role as 'coach' | 'client') || 'client';

  const steps: OnboardingStep[] = [
    {
      id: 0,
      title: 'Welcome',
      description: 'Welcome to Arete',
      component: WelcomeStep,
      required: true
    },
    {
      id: 1,
      title: 'Profile',
      description: 'Complete your profile',
      component: ProfileSetupStep,
      required: false
    },
    {
      id: 2,
      title: 'Dashboard',
      description: 'Explore your dashboard',
      component: DashboardTourStep,
      required: true
    },
    {
      id: 3,
      title: 'First Action',
      description: 'Take your first action',
      component: FirstActionStep,
      required: false
    },
    {
      id: 4,
      title: 'Complete',
      description: 'Setup complete',
      component: CompletionStep,
      required: true
    }
  ];

  useEffect(() => {
    if (user) {
      fetchOnboardingState();
    }
  }, [user]);

  const fetchOnboardingState = async () => {
    try {
      const token = await getAuthToken();
      const response = await fetch('http://localhost:8000/api/v1/users/me/onboarding', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        const state = data.onboarding_state;
        setOnboardingState(state);
        
        // Show onboarding if not completed
        if (!state.completed) {
          setIsVisible(true);
          setCurrentStep(state.current_step || 0);
          
          // Start onboarding if not started
          if (!state.started_at) {
            await startOnboarding();
          }
        }
      }
    } catch (error) {
      console.error('Error fetching onboarding state:', error);
    } finally {
      setLoading(false);
    }
  };

  const startOnboarding = async () => {
    try {
      const token = await getAuthToken();
      await fetch('http://localhost:8000/api/v1/users/me/onboarding/start', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
    } catch (error) {
      console.error('Error starting onboarding:', error);
    }
  };

  const completeStep = async (stepId: number) => {
    try {
      const token = await getAuthToken();
      await fetch(`http://localhost:8000/api/v1/users/me/onboarding/step/${stepId}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
    } catch (error) {
      console.error('Error completing step:', error);
    }
  };

  const completeOnboarding = async () => {
    try {
      const token = await getAuthToken();
      await fetch('http://localhost:8000/api/v1/users/me/onboarding/complete', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      setIsVisible(false);
    } catch (error) {
      console.error('Error completing onboarding:', error);
    }
  };

  const handleNext = async () => {
    await completeStep(currentStep);
    
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      await completeOnboarding();
    }
  };

  const handleSkip = async () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      await completeOnboarding();
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleClose = async () => {
    await completeOnboarding();
  };

  if (loading || !isVisible || !user) {
    return null;
  }

  const CurrentStepComponent = steps[currentStep]?.component;
  const progress = ((currentStep + 1) / steps.length) * 100;

  return (
    <div className="fixed inset-0 bg-black/75 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-md bg-white shadow-2xl border border-gray-200">
        <CardHeader className="relative bg-white">
          <Button
            variant="ghost"
            size="sm"
            className="absolute right-0 top-0"
            onClick={handleClose}
          >
            <X className="h-4 w-4" />
          </Button>
          
          <div className="space-y-2">
            <CardTitle className="text-lg">
              {steps[currentStep]?.title}
            </CardTitle>
            <CardDescription>
              Step {currentStep + 1} of {steps.length}
            </CardDescription>
            <Progress value={progress} className="w-full" />
          </div>
        </CardHeader>
        
        <CardContent className="space-y-6 bg-white">
          {CurrentStepComponent && (
            <CurrentStepComponent
              onNext={handleNext}
              onSkip={handleSkip}
              userRole={userRole}
            />
          )}
          
          {currentStep > 0 && (
            <div className="flex justify-between">
              <Button variant="ghost" onClick={handlePrevious}>
                <ArrowLeft className="mr-2 h-4 w-4" /> Previous
              </Button>
              <div></div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}