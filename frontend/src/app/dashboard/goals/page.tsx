"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useAuth } from "@/context/AuthContext";
import { PageHeader } from "@/components/navigation/NavigationUtils";

// Types based on the backend schemas
interface Goal {
  id: string;
  user_id: string;
  goal_statement: string;
  success_vision: string;
  progress_emoji: string;
  progress_notes?: string;
  progress_history: ProgressEntry[];
  ai_suggested: boolean;
  source_documents: string[];
  status: string;
  tags: string[];
  created_at: string;
  updated_at: string;
}

interface ProgressEntry {
  emoji: string;
  notes?: string;
  timestamp: string;
}

interface GoalSuggestion {
  goal_statement: string;
  success_vision: string;
  source_documents: string[];
}

interface Document {
  id: string;
  file_name: string;
  category: string;
  is_processed: boolean;
}

// Progress emoji options for easy selection
const PROGRESS_EMOJIS = [
  { emoji: "😐", label: "Neutral" },
  { emoji: "😊", label: "Happy" },
  { emoji: "🎉", label: "Celebrating" },
  { emoji: "💪", label: "Motivated" },
  { emoji: "🤔", label: "Thinking" },
  { emoji: "😤", label: "Determined" },
  { emoji: "😅", label: "Challenged" },
  { emoji: "🔥", label: "On Fire" },
  { emoji: "🌟", label: "Inspired" },
  { emoji: "🎯", label: "Focused" }
];

export default function GoalsDashboardPage() {
  const { getAuthToken, isAuthenticated, user } = useAuth();
  
  // State management
  const [currentView, setCurrentView] = useState<'choice' | 'create' | 'inspiration'>('choice');
  const [goals, setGoals] = useState<Goal[]>([]);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [goalSuggestions, setGoalSuggestions] = useState<GoalSuggestion[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Form state
  const [goalStatement, setGoalStatement] = useState("");
  const [successVision, setSuccessVision] = useState("");
  // const [selectedDocuments, setSelectedDocuments] = useState<string[]>([]);

  // Fetch user's goals and documents on component mount
  useEffect(() => {
    console.log('useEffect triggered - isAuthenticated:', isAuthenticated, 'user:', user);
    if (isAuthenticated && user) {
      console.log('User is authenticated, fetching data...');
      fetchGoals();
      fetchDocuments();
    } else {
      console.log('User not authenticated yet, waiting...');
    }
  }, [isAuthenticated, user]); // eslint-disable-line react-hooks/exhaustive-deps

  const fetchGoals = async () => {
    try {
      console.log('Attempting to fetch goals...');
      const token = await getAuthToken();
      console.log('Auth token:', token ? 'Available' : 'Not available');
      
      if (!token) {
        console.error('No authentication token available');
        setError('Authentication token not available. Please try refreshing the page or logging in again.');
        return;
      }

      const response = await fetch('http://localhost:8000/api/v1/goals/', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch goals: ${response.status}`);
      }

      const goalsData = await response.json();
      setGoals(goalsData);
      console.log('Goals fetched successfully:', goalsData.length);
    } catch (error) {
      console.error('Error fetching goals:', error);
      setError(error instanceof Error ? error.message : 'Failed to fetch goals');
    }
  };

  const fetchDocuments = async () => {
    try {
      const token = await getAuthToken();
      if (!token) return;

      const response = await fetch('http://localhost:8000/api/v1/documents/', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const documentsData = await response.json();
        setDocuments(documentsData.filter((doc: Document) => doc.is_processed));
      }
    } catch (error) {
      console.error('Error fetching documents:', error);
    }
  };

  const handleCreateGoal = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!goalStatement.trim() || !successVision.trim()) return;

    setIsLoading(true);
    setError(null);

    try {
      const token = await getAuthToken();
      if (!token) throw new Error('Authentication token not available');

      const response = await fetch('http://localhost:8000/api/v1/goals/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          goal_statement: goalStatement,
          success_vision: successVision,
          progress_emoji: "😐",
          ai_suggested: false,
          source_documents: [],
          tags: []
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to create goal');
      }

      // Reset form and refresh goals
      setGoalStatement("");
      setSuccessVision("");
      setCurrentView('choice');
      await fetchGoals();
    } catch (error) {
      console.error('Error creating goal:', error);
      setError(error instanceof Error ? error.message : 'Failed to create goal');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGetInspiration = async () => {
    if (documents.length === 0) {
      setError('No processed documents available for inspiration. Please upload and process some documents first.');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const token = await getAuthToken();
      if (!token) throw new Error('Authentication token not available');

      // Use all processed documents for suggestions
      const documentIds = documents.map(doc => doc.id);

      const response = await fetch('http://localhost:8000/api/v1/goals/suggestions', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(documentIds),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to get goal suggestions');
      }

      const suggestions = await response.json();
      setGoalSuggestions(suggestions);
      setCurrentView('inspiration');
    } catch (error) {
      console.error('Error getting goal suggestions:', error);
      setError(error instanceof Error ? error.message : 'Failed to get goal suggestions');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateFromSuggestion = async (suggestion: GoalSuggestion) => {
    setIsLoading(true);
    setError(null);

    try {
      const token = await getAuthToken();
      if (!token) throw new Error('Authentication token not available');

      const response = await fetch('http://localhost:8000/api/v1/goals/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          goal_statement: suggestion.goal_statement,
          success_vision: suggestion.success_vision,
          progress_emoji: "😐",
          ai_suggested: true,
          source_documents: suggestion.source_documents,
          tags: []
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to create goal from suggestion');
      }

      // Reset and refresh
      setCurrentView('choice');
      setGoalSuggestions([]);
      await fetchGoals();
    } catch (error) {
      console.error('Error creating goal from suggestion:', error);
      setError(error instanceof Error ? error.message : 'Failed to create goal from suggestion');
    } finally {
      setIsLoading(false);
    }
  };

  const handleUpdateProgress = async (goalId: string, emoji: string) => {
    try {
      const token = await getAuthToken();
      if (!token) throw new Error('Authentication token not available');

      const response = await fetch(`http://localhost:8000/api/v1/goals/${goalId}/progress`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          emoji: emoji,
          notes: null
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to update progress');
      }

      // Refresh goals to show updated progress
      await fetchGoals();
    } catch (error) {
      console.error('Error updating progress:', error);
      setError(error instanceof Error ? error.message : 'Failed to update progress');
    }
  };

  // Separate goals into categories
  const activeGoals = goals.filter(goal => goal.status === 'active');
  const celebratingGoals = goals.filter(goal => goal.progress_emoji === '🎉' || goal.status === 'completed');

  return (
    <div>
      <PageHeader />
      <div className="space-y-6">

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 text-red-800 border border-red-200 rounded-md">
            <p className="font-medium">Error</p>
            <p className="text-sm">{error}</p>
            <Button 
              onClick={() => setError(null)}
              variant="outline"
              size="sm"
              className="mt-2"
            >
              Dismiss
            </Button>
          </div>
        )}

        {/* Choice-Driven Workflow */}
        {currentView === 'choice' && (
          <div className="space-y-8">
            {/* Choice Buttons */}
            <Card>
              <CardHeader>
                <CardTitle>What would you like to do?</CardTitle>
                <CardDescription>
                  Choose your path to goal creation and management
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Button
                    onClick={() => setCurrentView('create')}
                    variant="outline"
                    className="h-24 flex flex-col items-center justify-center space-y-2"
                  >
                    <span className="text-2xl">🎯</span>
                    <span className="font-medium">I know what goals I want to work on</span>
                  </Button>
                  <Button
                    onClick={handleGetInspiration}
                    variant="outline"
                    className="h-24 flex flex-col items-center justify-center space-y-2"
                    disabled={isLoading}
                  >
                    <span className="text-2xl">💡</span>
                    <span className="font-medium">
                      {isLoading ? 'Getting inspiration...' : "I'd like some inspiration"}
                    </span>
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Goals Display */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Actively Working Goals */}
              <div>
                <h3 className="text-xl font-semibold text-gray-900 mb-4">
                  Actively Working ({activeGoals.length})
                </h3>
                <div className="space-y-4">
                  {activeGoals.length === 0 ? (
                    <Card>
                      <CardContent className="text-center py-8">
                        <div className="text-4xl mb-2">🎯</div>
                        <p className="text-gray-600">No active goals yet</p>
                        <p className="text-sm text-gray-500">Create your first goal to get started</p>
                      </CardContent>
                    </Card>
                  ) : (
                    activeGoals.map((goal) => (
                      <Card key={goal.id} className="hover:shadow-lg transition-shadow">
                        <CardHeader className="pb-3">
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <CardTitle className="text-lg font-medium text-gray-900">
                                {goal.goal_statement}
                              </CardTitle>
                              <CardDescription className="mt-1">
                                {goal.success_vision}
                              </CardDescription>
                            </div>
                            <div className="text-2xl ml-4">
                              {goal.progress_emoji}
                            </div>
                          </div>
                        </CardHeader>
                        <CardContent className="pt-0">
                          <div className="space-y-3">
                            {goal.progress_notes && (
                              <p className="text-sm text-gray-600 italic">
                                "{goal.progress_notes}"
                              </p>
                            )}
                            <div>
                              <Label className="text-xs font-medium text-gray-500 mb-2 block">
                                Update Progress Emotion
                              </Label>
                              <div className="flex flex-wrap gap-2">
                                {PROGRESS_EMOJIS.map((option) => (
                                  <Button
                                    key={option.emoji}
                                    variant={goal.progress_emoji === option.emoji ? "default" : "outline"}
                                    size="sm"
                                    onClick={() => handleUpdateProgress(goal.id, option.emoji)}
                                    className="text-lg px-3 py-1"
                                    title={option.label}
                                  >
                                    {option.emoji}
                                  </Button>
                                ))}
                              </div>
                            </div>
                            {goal.ai_suggested && (
                              <div className="flex items-center space-x-1 text-xs text-blue-600">
                                <span>🤖</span>
                                <span>AI-suggested goal</span>
                              </div>
                            )}
                          </div>
                        </CardContent>
                      </Card>
                    ))
                  )}
                </div>
              </div>

              {/* Celebrating Goals */}
              <div>
                <h3 className="text-xl font-semibold text-gray-900 mb-4">
                  Celebrating ({celebratingGoals.length})
                </h3>
                <div className="space-y-4">
                  {celebratingGoals.length === 0 ? (
                    <Card>
                      <CardContent className="text-center py-8">
                        <div className="text-4xl mb-2">🎉</div>
                        <p className="text-gray-600">No celebrations yet</p>
                        <p className="text-sm text-gray-500">Goals with 🎉 progress will appear here</p>
                      </CardContent>
                    </Card>
                  ) : (
                    celebratingGoals.map((goal) => (
                      <Card key={goal.id} className="border-green-200 bg-green-50">
                        <CardHeader className="pb-3">
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <CardTitle className="text-lg font-medium text-gray-900">
                                {goal.goal_statement}
                              </CardTitle>
                              <CardDescription className="mt-1">
                                {goal.success_vision}
                              </CardDescription>
                            </div>
                            <div className="text-2xl ml-4">
                              {goal.progress_emoji}
                            </div>
                          </div>
                        </CardHeader>
                        <CardContent className="pt-0">
                          {goal.progress_notes && (
                            <p className="text-sm text-gray-600 italic">
                              "{goal.progress_notes}"
                            </p>
                          )}
                          {goal.ai_suggested && (
                            <div className="flex items-center space-x-1 text-xs text-blue-600 mt-2">
                              <span>🤖</span>
                              <span>AI-suggested goal</span>
                            </div>
                          )}
                        </CardContent>
                      </Card>
                    ))
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Goal Creation Form */}
        {currentView === 'create' && (
          <Card>
            <CardHeader>
              <CardTitle>Create a New Goal</CardTitle>
              <CardDescription>
                Define what you want to work on and how you'll know it's working
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleCreateGoal} className="space-y-6">
                <div>
                  <Label htmlFor="goal-statement">What do you want to work on?</Label>
                  <Input
                    id="goal-statement"
                    value={goalStatement}
                    onChange={(e) => setGoalStatement(e.target.value)}
                    placeholder="e.g., Improve my public speaking confidence"
                    required
                    className="mt-1"
                  />
                </div>
                
                <div>
                  <Label htmlFor="success-vision">How will you know it's working?</Label>
                  <Textarea
                    id="success-vision"
                    value={successVision}
                    onChange={(e) => setSuccessVision(e.target.value)}
                    placeholder="e.g., I'll feel calm and confident when presenting to large groups, and I'll receive positive feedback about my clarity and engagement"
                    required
                    className="mt-1"
                    rows={3}
                  />
                </div>

                <div className="flex space-x-4">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => setCurrentView('choice')}
                  >
                    Back
                  </Button>
                  <Button
                    type="submit"
                    disabled={isLoading || !goalStatement.trim() || !successVision.trim()}
                  >
                    {isLoading ? 'Creating...' : 'Create Goal'}
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        )}

        {/* AI Inspiration View */}
        {currentView === 'inspiration' && (
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>AI-Powered Goal Suggestions</CardTitle>
                <CardDescription>
                  Based on your uploaded documents, here are some personalized goal suggestions
                </CardDescription>
              </CardHeader>
            </Card>

            {goalSuggestions.length === 0 ? (
              <Card>
                <CardContent className="text-center py-8">
                  <div className="text-4xl mb-2">🤖</div>
                  <p className="text-gray-600">No suggestions available</p>
                  <p className="text-sm text-gray-500">
                    Make sure you have uploaded and processed documents for personalized suggestions
                  </p>
                  <Button
                    onClick={() => setCurrentView('choice')}
                    variant="outline"
                    className="mt-4"
                  >
                    Back to Dashboard
                  </Button>
                </CardContent>
              </Card>
            ) : (
              <div className="space-y-4">
                {goalSuggestions.map((suggestion, index) => (
                  <Card key={index} className="hover:shadow-lg transition-shadow">
                    <CardHeader>
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <CardTitle className="text-lg font-medium text-gray-900">
                            {suggestion.goal_statement}
                          </CardTitle>
                          <CardDescription className="mt-2">
                            {suggestion.success_vision}
                          </CardDescription>
                        </div>
                        <div className="text-2xl ml-4">🤖</div>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="flex space-x-3">
                        <Button
                          onClick={() => handleCreateFromSuggestion(suggestion)}
                          disabled={isLoading}
                          size="sm"
                        >
                          {isLoading ? 'Creating...' : 'Create This Goal'}
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
                
                <div className="flex justify-center">
                  <Button
                    onClick={() => setCurrentView('choice')}
                    variant="outline"
                  >
                    Back to Dashboard
                  </Button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}