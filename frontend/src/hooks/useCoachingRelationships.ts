import { useState, useEffect, useCallback } from 'react';
import { useApiClient } from '@/utils/api';

interface Coach {
  id: string;
  name: string;
  email: string;
  bio?: string;
  specialties?: string[];
  location?: string;
  rating?: number;
  imageUrl?: string;
}

interface CoachingRelationship {
  id: string;
  coach_user_id: string;
  client_user_id: string;
  coach_email: string | null;
  client_email: string | null;
  status: 'pending' | 'active' | 'declined';
  created_at: string;
  updated_at: string;
}

interface CoachingRelationshipsResponse {
  pending: CoachingRelationship[];
  active: CoachingRelationship[];
}

interface TransformedRelationship {
  id: string;
  coach: Coach;
  status: 'pending' | 'active' | 'declined';
  createdAt: string;
  autoSendEnabled: boolean;
}

/**
 * Custom hook to fetch and manage coaching relationships for members
 */
export function useCoachingRelationships() {
  const { makeApiCall } = useApiClient();
  const [relationships, setRelationships] = useState<TransformedRelationship[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    const fetchRelationships = async () => {
      try {
        setIsLoading(true);
        setError(null);

        const response = await makeApiCall('/api/v1/member/coaching-relationships');
        
        if (!response.ok) {
          throw new Error(`Failed to fetch coaching relationships: ${response.status}`);
        }
        
        const data: CoachingRelationshipsResponse = await response.json();
        
        if (!isMounted) return;
        
        const processRelationships = (relationships: CoachingRelationship[]): TransformedRelationship[] => {
          return relationships.map((relationship) => ({
            id: relationship.id,
            coach: {
              id: relationship.coach_user_id,
              name: 'Your Coach', // Placeholder name
              email: relationship.coach_email || '',
            },
            status: relationship.status,
            createdAt: relationship.created_at,
            autoSendEnabled: false,
          }));
        };

        const activeRelationships = processRelationships(data.active);
        const pendingRelationships = processRelationships(data.pending);
        const transformedRelationships = [...activeRelationships, ...pendingRelationships];
        
        setRelationships(transformedRelationships);
      } catch (err) {
        if (!isMounted) return;
        const errorMessage = err instanceof Error ? err.message : 'Failed to fetch coaching relationships';
        setError(errorMessage);
        console.error('Error fetching coaching relationships:', err);
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    fetchRelationships();

    return () => {
      isMounted = false;
    };
  }, [makeApiCall]);

  const refetch = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);

      const response = await makeApiCall('/api/v1/member/coaching-relationships');
      
      if (!response.ok) {
        throw new Error(`Failed to fetch coaching relationships: ${response.status}`);
      }
      
      const data: CoachingRelationshipsResponse = await response.json();
      
      const processRelationships = (relationships: CoachingRelationship[]): TransformedRelationship[] => {
        return relationships.map((relationship) => ({
          id: relationship.id,
          coach: {
            id: relationship.coach_user_id,
            name: 'Your Coach', // Placeholder name
            email: relationship.coach_email || '',
          },
          status: relationship.status,
          createdAt: relationship.created_at,
          autoSendEnabled: false,
        }));
      };

      const activeRelationships = processRelationships(data.active);
      const pendingRelationships = processRelationships(data.pending);
      const transformedRelationships = [...activeRelationships, ...pendingRelationships];
      
      setRelationships(transformedRelationships);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch coaching relationships';
      setError(errorMessage);
      console.error('Error fetching coaching relationships:', err);
    } finally {
      setIsLoading(false);
    }
  }, [makeApiCall]);

  return {
    relationships,
    isLoading,
    error,
    refetch,
    // Helper functions
    hasActiveRelationships: () => relationships.some((rel: TransformedRelationship) => rel.status === 'active'),
    hasPendingRelationships: () => relationships.some((rel: TransformedRelationship) => rel.status === 'pending'),
    getActiveRelationships: () => relationships.filter((rel: TransformedRelationship) => rel.status === 'active'),
    getPendingRelationships: () => relationships.filter((rel: TransformedRelationship) => rel.status === 'pending')
  };
}