import { useAuth } from '@/context/AuthContext';

// Types
export interface Entry {
  id: string;
  title: string;
  content?: string;
  entry_type: 'fresh_thought' | 'session';
  created_at: string;
  session_date?: string;
  status: string;
  has_insights: boolean;
}

export interface DetectedGoal {
  goal_statement: string;
  confidence: number;
}

export interface FreemiumStatus {
  has_coach: boolean;
  entries_count: number;
  max_free_entries: number;
  entries_remaining: number;
  can_create_entries: boolean;
  can_access_insights: boolean;
  is_freemium: boolean;
}

export interface EntryFormData {
  content: string;
  session_date: string;
  input_method: 'paste' | 'upload';
  file_name?: string;
  title?: string;
  entry_type?: 'fresh_thought' | 'session';
  file?: File; // Add file property for PDF uploads
}

export interface CreateEntryResponse {
  id: string;
  detected_goals?: DetectedGoal[];
}

export interface GetEntriesParams {
  limit?: number;
  offset?: number;
}

export interface GetEntriesResponse {
  entries: Entry[];
}

/**
 * Centralized service for handling all entry-related API requests
 */
export class EntryService {
  private baseUrl: string;
  private getAuthToken: () => Promise<string | null>;

  constructor(getAuthToken: () => Promise<string | null>) {
    this.baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';
    this.getAuthToken = getAuthToken;
  }

  /**
   * Get the full API URL for an endpoint
   */
  private getApiUrl(endpoint: string): string {
    return `${this.baseUrl}/api/v1/entries${endpoint}`;
  }

  /**
   * Get common headers for API requests
   */
  private async getHeaders(): Promise<HeadersInit> {
    const token = await this.getAuthToken();
    if (!token) {
      throw new Error('Authentication token is required');
    }
    return {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    };
  }

  /**
   * Fetch entries with optional pagination
   */
  async getEntries(params: GetEntriesParams = {}): Promise<GetEntriesResponse> {
    const { limit, offset } = params;
    const queryParams = new URLSearchParams();
    
    if (limit !== undefined) {
      queryParams.append('limit', limit.toString());
    }
    if (offset !== undefined) {
      queryParams.append('offset', offset.toString());
    }

    const endpoint = queryParams.toString() ? `?${queryParams.toString()}` : '';
    const url = this.getApiUrl(endpoint);
    
    const response = await fetch(url, {
      method: 'GET',
      headers: await this.getHeaders(),
    });

    if (!response.ok) {
      throw new Error('Failed to fetch entries');
    }

    return await response.json();
  }

  /**
   * Create a new entry
   */
  async createEntry(entryData: EntryFormData): Promise<CreateEntryResponse> {
    const url = this.getApiUrl('');
    
    // Check if we have a PDF file to upload
    if (entryData.file && entryData.file.type === 'application/pdf') {
      // For PDF files, we need to use multipart form data and extract text on the backend
      const formData = new FormData();
      formData.append('file', entryData.file);
      formData.append('entry_type', entryData.entry_type || 'session');
      formData.append('session_date', entryData.session_date);
      formData.append('input_method', entryData.input_method);
      if (entryData.title) {
        formData.append('title', entryData.title);
      }
      
      const token = await this.getAuthToken();
      if (!token) {
        throw new Error('Authentication token is required');
      }
      
      const response = await fetch(`${this.baseUrl}/api/v1/entries/upload`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          // Don't set Content-Type for FormData, let browser set it with boundary
        },
        body: formData,
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail?.message || error.detail || 'Failed to create entry from file');
      }

      return await response.json();
    } else {
      // For text content, use the existing JSON approach
      const response = await fetch(url, {
        method: 'POST',
        headers: await this.getHeaders(),
        body: JSON.stringify(entryData),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail?.message || error.detail || 'Failed to create entry');
      }

      return await response.json();
    }
  }

  /**
   * Accept goal suggestions for an entry
   */
  async acceptGoals(entryId: string, acceptedGoalIndices: number[]): Promise<void> {
    const url = this.getApiUrl(`/${entryId}/accept-goals`);
    
    const response = await fetch(url, {
      method: 'POST',
      headers: await this.getHeaders(),
      body: JSON.stringify({
        accepted_goal_indices: acceptedGoalIndices
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to accept goals');
    }
  }

  /**
   * Get freemium status
   */
  async getFreemiumStatus(): Promise<FreemiumStatus> {
    const url = this.getApiUrl('/freemium/status');
    
    const response = await fetch(url, {
      method: 'GET',
      headers: await this.getHeaders(),
    });

    if (!response.ok) {
      throw new Error('Failed to fetch freemium status');
    }

    return await response.json();
  }
}

/**
 * Hook to get an instance of EntryService
 */
export function useEntryService(): EntryService {
  const { getAuthToken } = useAuth();
  return new EntryService(getAuthToken);
}