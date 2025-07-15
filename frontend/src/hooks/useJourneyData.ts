import { useState, useEffect } from 'react';
import { useAuth } from '@clerk/nextjs';

interface Insight {
  id: string;
  summary: string;
  categories: string[];
  key_points: string[];
  action_items: string[];
  created_at: string;
}

interface Reflection {
  id: string;
  title: string;
  original_filename: string;
  upload_date: string;
  insights_by_category: {
    understanding_myself?: string[];
    navigating_relationships?: string[];
    optimizing_performance?: string[];
    making_progress?: string[];
  };
}

export const useJourneyData = () => {
  const [insights, setInsights] = useState<Insight[]>([]);
  const [reflections, setReflections] = useState<Reflection[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const { getToken } = useAuth();

  const fetchInsights = async () => {
    try {
      const token = await getToken();
      const response = await fetch('http://localhost:8000/api/v1/reflections/insights', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setInsights(data.data.insights || []);
      }
    } catch (error) {
      console.error('Failed to fetch insights:', error);
    }
  };

  const fetchReflections = async () => {
    try {
      const token = await getToken();
      const response = await fetch('http://localhost:8000/api/v1/reflections/insights', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        // Convert insights to reflection format for compatibility
        const insights = data.data?.insights || [];
        const reflections = insights.map((insight: any) => ({
          id: insight.id,
          title: insight.title || `Reflection ${insight.id.slice(-8)}`, // Use AI-generated title
          original_filename: insight.original_filename || `reflection_${insight.id.slice(-8)}.txt`,
          upload_date: insight.created_at,
          insights_by_category: insight.insights_by_category || {
            understanding_myself: insight.key_points || [],
            navigating_relationships: [],
            optimizing_performance: insight.action_items || [],
            making_progress: []
          }
        }));
        setReflections(reflections);
      }
    } catch (error) {
      console.error('Failed to fetch reflections:', error);
      setReflections([]); // Safe fallback
    }
  };

  const uploadDocument = async (file: File): Promise<boolean> => {
    try {
      setUploading(true);
      const token = await getToken();
      
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await fetch('http://localhost:8000/api/v1/reflections/upload', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData
      });
      
      if (response.ok) {
        // Immediate refresh to show the document was uploaded
        await fetchInsights();
        await fetchReflections();
        
        // Poll for AI processing completion with exponential backoff
        let attempts = 0;
        const maxAttempts = 10;
        const pollForUpdates = async () => {
          attempts++;
          await fetchInsights();
          await fetchReflections();
          
          // Continue polling if we haven't reached max attempts
          if (attempts < maxAttempts) {
            const delay = Math.min(2000 * Math.pow(1.5, attempts - 1), 10000); // Max 10s delay
            setTimeout(pollForUpdates, delay);
          }
        };
        
        // Start polling after initial delay
        setTimeout(pollForUpdates, 3000);
        return true;
      }
      
      return false;
    } catch (error) {
      console.error('Upload failed:', error);
      return false;
    } finally {
      setUploading(false);
    }
  };

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await Promise.all([fetchInsights(), fetchReflections()]);
      setLoading(false);
    };
    
    loadData();
  }, []);

  return {
    insights,
    reflections,
    loading,
    uploading,
    uploadDocument,
    refetch: fetchInsights,
    hasInsights: insights.length > 0
  };
};