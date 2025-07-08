'use client';

import React, { useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

interface BaselineGeneratorProps {
  onBaselineGenerated?: () => void;
}

export const BaselineGenerator: React.FC<BaselineGeneratorProps> = ({ onBaselineGenerated }) => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const { getAuthToken } = useAuth();

  const handleGenerateBaseline = async () => {
    console.log('🚀 Starting baseline generation...');
    setIsGenerating(true);
    setError(null);
    setSuccess(false);

    try {
      const token = await getAuthToken();
      if (!token) {
        throw new Error('Authentication token not available');
      }
      console.log('✅ Got auth token');

      // First, get the current user's ID
      console.log('📡 Fetching user info...');
      const userResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/users/me`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!userResponse.ok) {
        throw new Error('Failed to get user information');
      }

      const userData = await userResponse.json();
      const userId = userData.id;
      console.log('✅ Got user ID:', userId);

      console.log('📡 Making POST request to generate baseline...');
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/analysis/generate-baseline`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId
        }),
      });

      console.log('📡 POST response status:', response.status);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.error('❌ POST request failed:', errorData);
        throw new Error(errorData.detail || 'Failed to generate baseline');
      }

      const responseData = await response.json();
      console.log('✅ Baseline generation successful:', responseData);
      
      setSuccess(true);
      onBaselineGenerated?.();
    } catch (err) {
      console.error('❌ Error in handleGenerateBaseline:', err);
      setError(err instanceof Error ? err.message : 'An unexpected error occurred');
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Generate New Baseline</CardTitle>
        <CardDescription>
          Create a comprehensive baseline analysis of your current documents and goals.
          This will help establish your starting point for coaching progress.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {error && (
          <div className="p-3 text-sm text-red-600 bg-red-50 border border-red-200 rounded-md">
            {error}
          </div>
        )}
        
        {success && (
          <div className="p-3 text-sm text-green-600 bg-green-50 border border-green-200 rounded-md">
            Baseline generated successfully! You can now view your baseline analysis.
          </div>
        )}

        <Button 
          onClick={handleGenerateBaseline}
          disabled={isGenerating}
          className="w-full"
        >
          {isGenerating ? 'Generating Baseline...' : 'Generate Baseline'}
        </Button>
      </CardContent>
    </Card>
  );
};