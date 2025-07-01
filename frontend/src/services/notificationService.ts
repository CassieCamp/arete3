export interface NotificationAction {
  label: string;
  url: string;
  action_type: string;
}

export interface Notification {
  id: string;
  user_id: string;
  title: string;
  message: string;
  type: string;
  priority: string;
  related_entity_id?: string;
  related_entity_type?: string;
  actions: NotificationAction[];
  metadata: Record<string, any>;
  is_read: boolean;
  is_dismissed: boolean;
  read_at?: string;
  dismissed_at?: string;
  delivery_method: string[];
  delivered_at?: string;
  created_at: string;
  expires_at?: string;
}

export interface NotificationListResponse {
  notifications: Notification[];
  total_count: number;
  unread_count: number;
  has_more: boolean;
}

class NotificationService {
  private baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  private async getAuthHeaders(token: string) {
    return {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    };
  }

  async getNotifications(
    token: string,
    limit: number = 20,
    offset: number = 0,
    unreadOnly: boolean = false
  ): Promise<NotificationListResponse> {
    const headers = await this.getAuthHeaders(token);
    
    const params = new URLSearchParams({
      limit: limit.toString(),
      offset: offset.toString(),
      unread_only: unreadOnly.toString(),
    });

    const response = await fetch(
      `${this.baseUrl}/api/v1/notifications/?${params}`,
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

  async getUnreadCount(token: string): Promise<number> {
    const headers = await this.getAuthHeaders(token);
    const url = `${this.baseUrl}/api/v1/notifications/unread-count`;
    
    // Enhanced error handling with connection diagnostics
    try {
      const response = await fetch(url, {
        method: 'GET',
        headers,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data.unread_count;
    } catch (error) {
      // Enhanced error diagnostics
      if (error instanceof TypeError && error.message.includes('fetch')) {
        // Network/connection error
        const connectionError = new Error(
          `🔌 Connection Error: Cannot reach backend server at ${this.baseUrl}. ` +
          `Please ensure the backend server is running on port 8000. ` +
          `Original error: ${error.message}`
        );
        connectionError.name = 'ConnectionError';
        throw connectionError;
      }
      
      // Re-throw other errors as-is
      throw error;
    }
  }

  async markAsRead(token: string, notificationId: string): Promise<void> {
    const headers = await this.getAuthHeaders(token);
    
    const response = await fetch(
      `${this.baseUrl}/api/v1/notifications/${notificationId}/read`,
      {
        method: 'POST',
        headers,
      }
    );

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }
  }

  async markAllAsRead(token: string): Promise<void> {
    const headers = await this.getAuthHeaders(token);
    
    const response = await fetch(
      `${this.baseUrl}/api/v1/notifications/mark-all-read`,
      {
        method: 'POST',
        headers,
      }
    );

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }
  }

  async dismissNotification(token: string, notificationId: string): Promise<void> {
    const headers = await this.getAuthHeaders(token);
    
    const response = await fetch(
      `${this.baseUrl}/api/v1/notifications/${notificationId}/dismiss`,
      {
        method: 'POST',
        headers,
      }
    );

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }
  }

  async getNotification(token: string, notificationId: string): Promise<Notification> {
    const headers = await this.getAuthHeaders(token);
    
    const response = await fetch(
      `${this.baseUrl}/api/v1/notifications/${notificationId}`,
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
}

export const notificationService = new NotificationService();