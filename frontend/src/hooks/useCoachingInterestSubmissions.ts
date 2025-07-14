import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '@clerk/nextjs';

export interface CoachingInterestSubmission {
  id: string;
  name: string;
  email: string;
  goals: string;
  email_permission: boolean;
  created_at: string;
}

export const useCoachingInterestSubmissions = () => {
  const [submissions, setSubmissions] = useState<CoachingInterestSubmission[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { getToken } = useAuth();

  const fetchSubmissions = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const token = await getToken();
      
      if (!token) {
        throw new Error('No authentication token available');
      }

      const response = await fetch('/api/v1/admin/coaching-interest/', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        if (response.status === 403) {
          throw new Error('Access denied: Admin role required');
        }
        throw new Error(`Failed to fetch coaching interest submissions: ${response.statusText}`);
      }

      const data = await response.json();
      setSubmissions(data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch submissions';
      setError(errorMessage);
      console.error('Error fetching coaching interest submissions:', err);
    } finally {
      setLoading(false);
    }
  }, [getToken]);

  useEffect(() => {
    fetchSubmissions();
  }, [fetchSubmissions]);

  return {
    submissions,
    loading,
    error,
    refetch: fetchSubmissions,
  };
};