"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useAuth } from "@/context/AuthContext";
import { PageHeader } from "@/components/ui/page-header";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { ThreeIconNav } from "@/components/navigation/ThreeIconNav";
import { User, MessageCircle, Calendar, Star, Clock, Users } from "lucide-react";

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

interface CoachInfo {
  name: string;
  email: string;
  specialties: string[];
  experience: string;
  rating: number;
  nextSession?: string;
}

export default function CoachPage() {
  const { user, isAuthenticated, getAuthToken } = useAuth();
  const [relationships, setRelationships] = useState<UserRelationships>({
    pending: [],
    active: []
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

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

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/coaching-relationships/`, {
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

  const respondToRequest = async (relationshipId: string, status: "active" | "declined") => {
    try {
      setLoading(true);
      setError(null);
      setSuccess(null);

      const token = await getAuthToken();
      if (!token) {
        throw new Error("No authentication token available");
      }

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/coaching-relationships/${relationshipId}/respond`, {
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

  const getCoachEmail = (relationship: CoachingRelationship) => {
    return relationship.coach_email || `Coach ${relationship.coach_user_id}`;
  };

  // Filter pending requests to only show incoming requests from coaches
  const incomingPendingRequests = relationships.pending.filter(relationship => {
    return relationship.client_user_id === user?.id;
  });

  // Get active coaching relationships where user is the client
  const activeCoachingRelationships = relationships.active.filter(relationship => {
    return relationship.client_user_id === user?.id;
  });

  // Mock coach data - in a real implementation, this would come from the backend
  const getCoachInfo = (relationship: CoachingRelationship): CoachInfo => {
    return {
      name: getCoachEmail(relationship).split('@')[0] || 'Your Coach',
      email: getCoachEmail(relationship),
      specialties: ['Leadership', 'Career Development', 'Goal Setting'],
      experience: '5+ years',
      rating: 4.8,
      nextSession: 'Tomorrow 2:00 PM'
    };
  };

  // Show loading while authentication is being determined
  if (isAuthenticated === undefined) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  // Show loading while user data is being loaded
  if (isAuthenticated && !user) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading user data...</p>
        </div>
      </div>
    );
  }

  // If not authenticated, show loading state
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Redirecting...</p>
        </div>
      </div>
    );
  }

  return (
    <DashboardLayout>
      <ThreeIconNav />
      <div className="container mx-auto px-4 py-8 md:pt-20 pb-20">
        <PageHeader
          icon={Users}
          title="Coach"
          subtitle="Connect with your coach and manage your coaching relationships"
        />
        
        <div className="w-full max-w-4xl mx-auto space-y-6">
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

        {/* Active Coach Relationships */}
        {activeCoachingRelationships.length > 0 && (
          <div className="space-y-4">
            {activeCoachingRelationships.map((relationship) => {
              const coachInfo = getCoachInfo(relationship);
              return (
                <Card key={relationship.id} className="bg-gradient-to-r from-primary/5 to-accent/5 dark:from-primary/10 dark:to-accent/10">
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-3">
                        <div className="h-12 w-12 bg-primary/10 rounded-full flex items-center justify-center">
                          <User className="h-6 w-6 text-primary" />
                        </div>
                        <div>
                          <CardTitle className="text-lg">{coachInfo.name}</CardTitle>
                          <CardDescription>{coachInfo.email}</CardDescription>
                        </div>
                      </div>
                      <Badge variant="secondary" className="bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400">
                        Active
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {/* Coach Details */}
                    <div className="grid md:grid-cols-2 gap-4">
                      <div>
                        <h4 className="font-medium text-sm text-muted-foreground mb-2">Specialties</h4>
                        <div className="flex flex-wrap gap-1">
                          {coachInfo.specialties.map((specialty, index) => (
                            <Badge key={index} variant="outline" className="text-xs">
                              {specialty}
                            </Badge>
                          ))}
                        </div>
                      </div>
                      <div>
                        <h4 className="font-medium text-sm text-muted-foreground mb-2">Experience</h4>
                        <p className="text-sm text-foreground">{coachInfo.experience}</p>
                      </div>
                    </div>

                    {/* Rating and Next Session */}
                    <div className="grid md:grid-cols-2 gap-4">
                      <div className="flex items-center gap-2">
                        <Star className="h-4 w-4 text-yellow-500 fill-current" />
                        <span className="text-sm font-medium">{coachInfo.rating}</span>
                        <span className="text-sm text-muted-foreground">rating</span>
                      </div>
                      {coachInfo.nextSession && (
                        <div className="flex items-center gap-2">
                          <Clock className="h-4 w-4 text-muted-foreground" />
                          <span className="text-sm text-foreground">{coachInfo.nextSession}</span>
                        </div>
                      )}
                    </div>

                    {/* Action Buttons */}
                    <div className="flex gap-2 pt-2">
                      <Button size="sm" className="flex items-center gap-2">
                        <MessageCircle className="h-4 w-4" />
                        Message Coach
                      </Button>
                      <Button size="sm" variant="outline" className="flex items-center gap-2">
                        <Calendar className="h-4 w-4" />
                        Schedule Session
                      </Button>
                    </div>

                    {/* Connection Info */}
                    <div className="pt-2 border-t border-border/50">
                      <p className="text-xs text-muted-foreground">
                        Connected since: {new Date(relationship.updated_at).toLocaleDateString()}
                      </p>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        )}

        {/* Pending Coach Invitations */}
        {incomingPendingRequests.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Coach Invitations</CardTitle>
              <CardDescription>
                You have received coaching invitations
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {incomingPendingRequests.map((relationship) => (
                  <div
                    key={relationship.id}
                    className="p-4 border border-border rounded-lg bg-primary/5"
                  >
                    <div className="flex justify-between items-start mb-3">
                      <div className="flex items-center gap-3">
                        <div className="h-10 w-10 bg-primary/10 rounded-full flex items-center justify-center">
                          <User className="h-5 w-5 text-primary" />
                        </div>
                        <div>
                          <p className="font-medium">{getCoachEmail(relationship)}</p>
                          <p className="text-sm text-muted-foreground">
                            Wants to be your coach
                          </p>
                          <p className="text-xs text-muted-foreground">
                            Invitation received: {new Date(relationship.created_at).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        onClick={() => respondToRequest(relationship.id, "active")}
                        disabled={loading}
                      >
                        Accept Coach
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
              </div>
            </CardContent>
          </Card>
        )}

        {/* No Coach State */}
        {activeCoachingRelationships.length === 0 && incomingPendingRequests.length === 0 && !loading && (
          <Card className="text-center py-8">
            <CardContent>
              <div className="flex flex-col items-center gap-4">
                <div className="h-16 w-16 bg-muted rounded-full flex items-center justify-center">
                  <User className="h-8 w-8 text-muted-foreground" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-foreground mb-2">No Coach Connected</h3>
                  <p className="text-muted-foreground mb-4">
                    You don't have a coach yet. A coach can help guide your growth journey and provide personalized insights.
                  </p>
                  <p className="text-sm text-muted-foreground">
                    Your coach will send you an invitation to connect. Once you accept, you'll be able to see their information and schedule sessions here.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Loading State */}
        {loading && (activeCoachingRelationships.length === 0 && incomingPendingRequests.length === 0) && (
          <Card>
            <CardContent className="py-8">
              <div className="text-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
                <p className="text-muted-foreground">Loading your coaching relationships...</p>
              </div>
            </CardContent>
          </Card>
        )}
        </div>
      </div>
    </DashboardLayout>
  );
}