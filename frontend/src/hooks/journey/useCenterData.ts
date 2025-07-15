import { useState, useEffect } from 'react';
import { useApiClient } from '@/utils/api';

interface CenterData {
  user_id: string;
  goals: any[];
  values: any[];
  energy_logs: any[];
  documents: any[];
  assessments: any[];
  data_summary: Record<string, number>;
}

interface UseCenterDataReturn {
  centerData: CenterData | null;
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

export const useCenterData = (): UseCenterDataReturn => {
  const { makeApiCall } = useApiClient();
  const [centerData, setCenterData] = useState<CenterData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchCenterData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await makeApiCall('/api/v1/journey/center-data');

      if (!response.ok) {
        throw new Error(`Failed to fetch center data: ${response.status}`);
      }

      const data = await response.json();
      setCenterData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
      setCenterData(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCenterData();
  }, [makeApiCall]);

  const refetch = () => {
    fetchCenterData();
  };

  return {
    centerData,
    loading,
    error,
    refetch,
  };
};