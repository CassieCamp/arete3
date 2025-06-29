"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAuth } from "@/context/AuthContext";
import { useRouter } from "next/navigation";
import { PageHeader } from "@/components/navigation/NavigationUtils";

// Types based on backend schemas
interface CoachingRelationship {
  id: string;
  coach_user_id: string;
  client_user_id: string;
  status: "pending" | "active" | "declined";
  created_at: string;
  updated_at: string;
  coach_email?: string;
  client_email?: string;
}

interface UserRelationships {
  pending: CoachingRelationship[];
  active: CoachingRelationship[];
}

export default function ConnectionsPage() {
  const { user, isAuthenticated, getAuthToken } = useAuth();
  const router = useRouter();
  const [clientEmail, setClientEmail] = useState("");
  const [relationships, setRelationships] = useState<UserRelationships>({
    pending: [],
    active: []
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Authentication is now handled by middleware

  // Fetch relationships on component mount
  useEffect(() => {
    if (isAuthenticated && user) {
      fetchRelationships();
    }
  }, [isAuthenticated, user]);

  const fetchRelationships = async () => {
    try {
      setLoading(true);
      const token = await getAuthToken();
      if (!token) {
        throw new Error("No authentication token available");
      }

      const response = await fetch("http://localhost:8000/api/v1/coaching-relationships/", {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to fetch relationships");
      }

      const data: UserRelationships = await response.json();
      setRelationships(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch relationships");
    } finally {
      setLoading(false);
    }
  };

  const sendConnectionRequest = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!clientEmail.trim()) {
      setError("Please enter a client email address");
      return;
    }

    try {
      setLoading(true);
      setError(null);
      setSuccess(null);

      const token = await getAuthToken();
      if (!token) {
        throw new Error("No authentication token available");
      }

      const response = await fetch("http://localhost:8000/api/v1/coaching-relationships/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({
          client_email: clientEmail,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to send connection request");
      }

      setSuccess("Connection request sent successfully!");
      setClientEmail("");
      // Refresh relationships to show the new request
      await fetchRelationships();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to send connection request");
    } finally {
      setLoading(false);
    }
  };

  const respondToRequest = async (relationshipId: string, status: "active" | "declined") => {
    try {
      setLoading(true);
      setError(null);
      setSuccess(null);

      const token = await getAuthToken();
      if (!token) {
        throw new Error("No authentication token available");
      }

      const response = await fetch(`http://localhost:8000/api/v1/coaching-relationships/${relationshipId}/respond`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({
          status: status,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to respond to request");
      }

      setSuccess(`Request ${status === "active" ? "accepted" : "declined"} successfully!`);
      // Refresh relationships to show updated status
      await fetchRelationships();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to respond to request");
    } finally {
      setLoading(false);
    }
  };

  const getOtherUserEmail = (relationship: CoachingRelationship) => {
    // Show the email of the other user in the relationship
    if (relationship.coach_user_id === user?.id) {
      // Current user is the coach, show client email
      return relationship.client_email || `Client ${relationship.client_user_id}`;
    } else {
      // Current user is the client, show coach email
      return relationship.coach_email || `Coach ${relationship.coach_user_id}`;
    }
  };

  const getRelationshipRole = (relationship: CoachingRelationship) => {
    return relationship.coach_user_id === user?.id ? "Coach" : "Client";
  };

  // Filter pending requests to only show incoming requests (requests where current user needs to respond)
  const incomingPendingRequests = relationships.pending.filter(relationship => {
    // Show requests where the current user is the client (receiving coach's invitation)
    // This means they can accept or decline
    return relationship.client_user_id === user?.id;
  });

  // Filter pending requests that the current user sent (for display purposes)
  const outgoingPendingRequests = relationships.pending.filter(relationship => {
    // Show requests where the current user is the coach (sent invitation to client)
    return relationship.coach_user_id === user?.id;
  });

  // Show loading while authentication is being determined
  if (isAuthenticated === undefined) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // Show loading while user data is being loaded
  if (isAuthenticated && !user) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading user data...</p>
        </div>
      </div>
    );
  }

  // If not authenticated, the useEffect will handle redirect
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto mb-4"></div>
          <p className="text-gray-600">Redirecting...</p>
        </div>
      </div>
    );
  }

  return (
    <div>
      <PageHeader />
      
      <div className="space-y-6">
        {/* Error and Success Messages */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
            <p className="text-red-800">{error}</p>
          </div>
        )}
        {success && (
          <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-md">
            <p className="text-green-800">{success}</p>
          </div>
        )}

        {/* Send Connection Request Form - Only visible for coaches */}
        {user?.role === 'coach' && (
          <Card className="mb-8">
            <CardHeader>
              <CardTitle>Send Connection Request</CardTitle>
              <CardDescription>
                Enter the email address of the client you'd like to invite
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={sendConnectionRequest} className="space-y-4">
                <div>
                  <Label htmlFor="clientEmail">Client Email Address</Label>
                  <Input
                    id="clientEmail"
                    type="email"
                    value={clientEmail}
                    onChange={(e) => setClientEmail(e.target.value)}
                    placeholder="Enter client email address"
                    disabled={loading}
                  />
                </div>
                <Button type="submit" disabled={loading}>
                  {loading ? "Sending..." : "Send Invitation"}
                </Button>
              </form>
            </CardContent>
          </Card>
        )}

        <div className="grid md:grid-cols-2 gap-8">
          {/* Pending Requests */}
          <Card>
            <CardHeader>
              <CardTitle>Pending Requests</CardTitle>
              <CardDescription>
                Connection requests and invitations
              </CardDescription>
            </CardHeader>
            <CardContent>
              {loading && (incomingPendingRequests.length === 0 && outgoingPendingRequests.length === 0) ? (
                <p className="text-gray-500">Loading...</p>
              ) : (incomingPendingRequests.length === 0 && outgoingPendingRequests.length === 0) ? (
                <p className="text-gray-500">No pending requests</p>
              ) : (
                <div className="space-y-4">
                  {/* Show incoming requests (where user can accept/decline) */}
                  {incomingPendingRequests.map((relationship) => (
                    <div
                      key={relationship.id}
                      className="p-4 border border-gray-200 rounded-lg bg-blue-50"
                    >
                      <div className="flex justify-between items-start mb-3">
                        <div>
                          <p className="font-medium">{getOtherUserEmail(relationship)}</p>
                          <p className="text-sm text-gray-600">
                            Role: {getRelationshipRole(relationship)}
                          </p>
                          <p className="text-xs text-gray-500">
                            Invitation received: {new Date(relationship.created_at).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <Button
                          size="sm"
                          onClick={() => respondToRequest(relationship.id, "active")}
                          disabled={loading}
                        >
                          Accept
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => respondToRequest(relationship.id, "declined")}
                          disabled={loading}
                        >
                          Decline
                        </Button>
                      </div>
                    </div>
                  ))}
                  
                  {/* Show outgoing requests (where user is waiting for response) */}
                  {outgoingPendingRequests.map((relationship) => (
                    <div
                      key={relationship.id}
                      className="p-4 border border-gray-200 rounded-lg bg-yellow-50"
                    >
                      <div className="flex justify-between items-start mb-3">
                        <div>
                          <p className="font-medium">{getOtherUserEmail(relationship)}</p>
                          <p className="text-sm text-gray-600">
                            Role: {getRelationshipRole(relationship)}
                          </p>
                          <p className="text-xs text-gray-500">
                            Invitation sent: {new Date(relationship.created_at).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                      <p className="text-sm text-gray-500">Waiting for client response...</p>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Active Connections */}
          <Card>
            <CardHeader>
              <CardTitle>Active Connections</CardTitle>
              <CardDescription>
                Your established coaching relationships
              </CardDescription>
            </CardHeader>
            <CardContent>
              {loading && relationships.active.length === 0 ? (
                <p className="text-gray-500">Loading...</p>
              ) : relationships.active.length === 0 ? (
                <p className="text-gray-500">No active connections</p>
              ) : (
                <div className="space-y-4">
                  {relationships.active.map((relationship) => (
                    <div
                      key={relationship.id}
                      className="p-4 border border-gray-200 rounded-lg bg-green-50"
                    >
                      <div className="flex justify-between items-start">
                        <div>
                          <p className="font-medium">{getOtherUserEmail(relationship)}</p>
                          <p className="text-sm text-gray-600">
                            Role: {getRelationshipRole(relationship)}
                          </p>
                          <p className="text-xs text-gray-500">
                            Connected: {new Date(relationship.updated_at).toLocaleDateString()}
                          </p>
                        </div>
                        <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                          Active
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}