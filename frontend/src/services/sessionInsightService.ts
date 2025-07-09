export interface SessionInsightCompetency {
  category: string;
  items: string[];
}

export interface Celebration {
  description: string;
  significance: string;
  evidence: string[];
}

export interface Intention {
  behavior_change: string;
  commitment_level: string;
  timeline?: string;
  support_needed: string[];
}

export interface ClientDiscovery {
  insight: string;
  depth_level: string;
  emotional_response: string;
  evidence: string[];
}

export interface GoalProgress {
  goal_area: string;
  progress_description: string;
  progress_level: string;
  barriers_identified: string[];
  next_steps: string[];
}

export interface CoachingPresence {
  client_engagement_level: string;
  rapport_quality: string;
  trust_indicators: string[];
  partnership_dynamics: string;
}

export interface PowerfulQuestion {
  question: string;
  impact_description: string;
  client_response_summary: string;
  breakthrough_level: string;
}

export interface ActionItem {
  action: string;
  timeline?: string;
  accountability_measure?: string;
  client_commitment_level: string;
}

export interface EmotionalShift {
  initial_state: string;
  final_state: string;
  shift_description: string;
  catalyst: string;
}

export interface ValuesBeliefs {
  type: string;
  description: string;
  impact_on_goals: string;
  exploration_depth: string;
}

export interface CommunicationPattern {
  processing_style: string;
  expression_patterns: string[];
  communication_preferences: string[];
  notable_changes: string[];
}

export interface SessionInsight {
  id: string;
  coaching_relationship_id?: string;
  client_user_id: string;
  coach_user_id?: string;
  session_date?: string;
  session_title?: string;
  session_summary?: string;
  key_themes: string[];
  overall_session_quality?: string;
  status: string;
  created_at: string;
  completed_at?: string;
  celebration_count?: number;
  intention_count?: number;
  discovery_count?: number;
  action_item_count?: number;
  // Additional properties for unpaired insights
  title?: string;
  content?: string;
  shared_with?: string[];
}

export interface SessionInsightDetail extends SessionInsight {
  celebration?: Celebration;
  intention?: Intention;
  client_discoveries: ClientDiscovery[];
  goal_progress: GoalProgress[];
  coaching_presence?: CoachingPresence;
  powerful_questions: PowerfulQuestion[];
  action_items: ActionItem[];
  emotional_shifts: EmotionalShift[];
  values_beliefs: ValuesBeliefs[];
  communication_patterns?: CommunicationPattern;
}

export interface CreateSessionInsightRequest {
  coaching_relationship_id: string;
  session_date?: string;
  session_title?: string;
  transcript_text?: string;
}

export interface SessionInsightListResponse {
  insights: SessionInsight[];
  total_count: number;
  relationship_id: string;
  client_name: string;
  coach_name: string;
}

// New interfaces for unpaired insights
export interface CreateUnpairedInsightRequest {
  title: string;
  content: string;
  tags?: string[];
}

export interface CreateUnpairedTranscriptInsightRequest {
  session_date?: string;
  session_title?: string;
  transcript_text: string;
}

export interface ShareInsightRequest {
  coach_email: string;
  message?: string;
}

export interface MyInsightsResponse {
  my_insights: SessionInsight[];
  shared_with_me: SessionInsight[];
}

class SessionInsightService {
  private baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  private async getAuthHeaders(token: string) {
    return {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    };
  }

  async createSessionInsightFromFile(
    token: string,
    data: {
      coaching_relationship_id: string;
      session_date?: string;
      session_title?: string;
      transcript_file: File;
    }
  ): Promise<SessionInsight> {
    const formData = new FormData();
    formData.append('coaching_relationship_id', data.coaching_relationship_id);
    if (data.session_date) {
      formData.append('session_date', data.session_date);
    }
    if (data.session_title) {
      formData.append('session_title', data.session_title);
    }
    formData.append('transcript_file', data.transcript_file);

    const response = await fetch(`${this.baseUrl}/api/v1/session-insights/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async createSessionInsightFromText(
    token: string,
    data: CreateSessionInsightRequest
  ): Promise<SessionInsight> {
    const headers = await this.getAuthHeaders(token);
    
    const response = await fetch(`${this.baseUrl}/api/v1/session-insights/from-text`, {
      method: 'POST',
      headers,
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async getSessionInsightsForRelationship(
    token: string,
    relationshipId: string,
    limit: number = 20,
    offset: number = 0
  ): Promise<SessionInsightListResponse> {
    const headers = await this.getAuthHeaders(token);
    
    const params = new URLSearchParams({
      limit: limit.toString(),
      offset: offset.toString(),
    });

    const response = await fetch(
      `${this.baseUrl}/api/v1/session-insights/relationship/${relationshipId}?${params}`,
      {
        method: 'GET',
        headers,
      }
    );

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async getSessionInsightDetail(
    token: string,
    insightId: string
  ): Promise<SessionInsightDetail> {
    const headers = await this.getAuthHeaders(token);
    
    const response = await fetch(`${this.baseUrl}/api/v1/session-insights/${insightId}`, {
      method: 'GET',
      headers,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async deleteSessionInsight(token: string, insightId: string): Promise<void> {
    const headers = await this.getAuthHeaders(token);
    
    const response = await fetch(`${this.baseUrl}/api/v1/session-insights/${insightId}`, {
      method: 'DELETE',
      headers,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }
  }

  // New methods for unpaired insights
  async createUnpairedInsight(
    token: string,
    data: CreateUnpairedInsightRequest
  ): Promise<SessionInsight> {
    const headers = await this.getAuthHeaders(token);
    
    const response = await fetch(`${this.baseUrl}/api/v1/session-insights/unpaired/from-text`, {
      method: 'POST',
      headers,
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async createUnpairedInsightFromTranscript(
    token: string,
    data: CreateUnpairedTranscriptInsightRequest
  ): Promise<SessionInsight> {
    const headers = await this.getAuthHeaders(token);
    
    const response = await fetch(`${this.baseUrl}/api/v1/session-insights/unpaired/from-text`, {
      method: 'POST',
      headers,
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async createUnpairedInsightFromFile(
    token: string,
    data: {
      session_date?: string;
      session_title?: string;
      transcript_file: File;
    }
  ): Promise<SessionInsight> {
    const formData = new FormData();
    if (data.session_date) {
      formData.append('session_date', data.session_date);
    }
    if (data.session_title) {
      formData.append('session_title', data.session_title);
    }
    formData.append('transcript_file', data.transcript_file);

    const response = await fetch(`${this.baseUrl}/api/v1/session-insights/unpaired/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async getMyInsights(token: string): Promise<SessionInsight[]> {
    const headers = await this.getAuthHeaders(token);
    
    const response = await fetch(`${this.baseUrl}/api/v1/session-insights/my-insights`, {
      method: 'GET',
      headers,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async shareInsight(
    token: string,
    insightId: string,
    data: ShareInsightRequest
  ): Promise<void> {
    const headers = await this.getAuthHeaders(token);
    
    const response = await fetch(`${this.baseUrl}/api/v1/session-insights/${insightId}/share`, {
      method: 'POST',
      headers,
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }
  }

  async updateInsight(
    token: string,
    insightId: string,
    data: Partial<CreateUnpairedInsightRequest>
  ): Promise<SessionInsight> {
    const headers = await this.getAuthHeaders(token);
    
    const response = await fetch(`${this.baseUrl}/api/v1/session-insights/${insightId}`, {
      method: 'PUT',
      headers,
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return response.json();
  }
}

export const sessionInsightService = new SessionInsightService();