import { useAuth } from "@/context/AuthContext";

const apiClient = {
  async get(url: string, authToken: string, orgId?: string) {
    const headers: HeadersInit = {
      "Content-Type": "application/json",
      Authorization: `Bearer ${authToken}`,
    };
    if (orgId) {
      headers["X-Org-Id"] = orgId;
    }
    const response = await fetch(`/api/v1${url}`, {
      method: "GET",
      headers,
    });
    if (!response.ok) {
      throw new Error(`Failed to fetch ${url}: ${response.statusText}`);
    }
    return response.json();
  },

  async post(url: string, authToken: string, body: any, orgId?: string) {
    const headers: HeadersInit = {
      "Content-Type": "application/json",
      Authorization: `Bearer ${authToken}`,
    };
    if (orgId) {
      headers["X-Org-Id"] = orgId;
    }
    const response = await fetch(`/api/v1${url}`, {
      method: "POST",
      headers,
      body: JSON.stringify(body),
    });
    if (!response.ok) {
      throw new Error(`Failed to post to ${url}: ${response.statusText}`);
    }
    return response.json();
  },

  async put(url: string, authToken: string, body: any, orgId?: string) {
    const headers: HeadersInit = {
      "Content-Type": "application/json",
      Authorization: `Bearer ${authToken}`,
    };
    if (orgId) {
      headers["X-Org-Id"] = orgId;
    }
    const response = await fetch(`/api/v1${url}`, {
      method: "PUT",
      headers,
      body: JSON.stringify(body),
    });
    if (!response.ok) {
      throw new Error(`Failed to put to ${url}: ${response.statusText}`);
    }
    return response.json();
  },

  async delete(url: string, authToken: string, orgId?: string) {
    const headers: HeadersInit = {
      "Content-Type": "application/json",
      Authorization: `Bearer ${authToken}`,
    };
    if (orgId) {
      headers["X-Org-Id"] = orgId;
    }
    const response = await fetch(`/api/v1${url}`, {
      method: "DELETE",
      headers,
    });
    if (!response.ok) {
      throw new Error(`Failed to delete ${url}: ${response.statusText}`);
    }
    return response.json();
  },
};

export default apiClient;