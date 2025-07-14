"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useAuth } from "@/context/AuthContext";
import { useUser } from "@clerk/nextjs";
import { PageHeader } from "@/components/ui/page-header";
import { AppLayout } from "@/components/layout/AppLayout";
import { ThreeIconNav } from "@/components/navigation/ThreeIconNav";
import { User, Edit, Save, Star, MapPin, Clock, Award, Users } from "lucide-react";

/**
 * Coach Profile Management Page
 * 
 * This is the internal coach interface for managing their own profile.
 * Components are designed for reusability across:
 * 1. Coach self-profile management (/coach/profile) - THIS PAGE
 * 2. Member "Coaching" view (/coaching) showing assigned coaches
 * 3. Future public coach profiles (/coaches/:coachId)
 */

interface CoachProfile {
  id: string;
  name: string;
  email: string;
  bio: string;
  specialties: string[];
  experience: string;
  location: string;
  hourlyRate: string;
  availability: string;
  certifications: string[];
  languages: string[];
  rating?: number;
  totalSessions?: number;
  yearsExperience?: number;
}

export default function CoachProfilePage() {
  const { user, isAuthenticated, getAuthToken } = useAuth();
  const { user: clerkUser } = useUser();
  const [profile, setProfile] = useState<CoachProfile>({
    id: '',
    name: '',
    email: '',
    bio: '',
    specialties: [],
    experience: '',
    location: '',
    hourlyRate: '',
    availability: '',
    certifications: [],
    languages: [],
  });
  const [isEditing, setIsEditing] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Form state for editing
  const [editForm, setEditForm] = useState<CoachProfile>(profile);

  useEffect(() => {
    if (isAuthenticated && user) {
      loadProfile();
    }
  }, [isAuthenticated, user]);

  const loadProfile = async () => {
    try {
      setLoading(true);
      // TODO: Replace with actual API call
      // For now, use mock data with user info from Clerk
      const mockProfile: CoachProfile = {
        id: user?.id || '',
        name: clerkUser?.fullName || clerkUser?.emailAddresses[0]?.emailAddress?.split('@')[0] || 'Coach',
        email: clerkUser?.emailAddresses[0]?.emailAddress || '',
        bio: 'Passionate about helping individuals unlock their potential and achieve their goals through personalized coaching strategies.',
        specialties: ['Leadership Development', 'Career Coaching', 'Goal Setting', 'Performance Optimization'],
        experience: '5+ years of professional coaching experience',
        location: 'San Francisco, CA',
        hourlyRate: '$150',
        availability: 'Monday-Friday, 9 AM - 6 PM PST',
        certifications: ['ICF Certified Coach', 'Leadership Development Certificate'],
        languages: ['English', 'Spanish'],
        rating: 4.8,
        totalSessions: 247,
        yearsExperience: 5
      };
      
      setProfile(mockProfile);
      setEditForm(mockProfile);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load profile");
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setLoading(true);
      setError(null);
      setSuccess(null);

      // TODO: Replace with actual API call
      // const token = await getAuthToken();
      // const response = await fetch(`/api/v1/coach/profile`, {
      //   method: 'PUT',
      //   headers: {
      //     'Content-Type': 'application/json',
      //     'Authorization': `Bearer ${token}`,
      //   },
      //   body: JSON.stringify(editForm),
      // });

      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setProfile(editForm);
      setIsEditing(false);
      setSuccess("Profile updated successfully!");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update profile");
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    setEditForm(profile);
    setIsEditing(false);
    setError(null);
  };

  const addSpecialty = (specialty: string) => {
    if (specialty.trim() && !editForm.specialties.includes(specialty.trim())) {
      setEditForm({
        ...editForm,
        specialties: [...editForm.specialties, specialty.trim()]
      });
    }
  };

  const removeSpecialty = (specialty: string) => {
    setEditForm({
      ...editForm,
      specialties: editForm.specialties.filter(s => s !== specialty)
    });
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
    <AppLayout>
      <ThreeIconNav />
      <div className="container mx-auto px-4 py-8 md:pt-20 pb-20">
        <PageHeader
          icon={User}
          title="Profile"
          subtitle="Manage your coaching profile and professional information"
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

          {/* Profile Header Card */}
          <Card>
            <CardHeader>
              <div className="flex justify-between items-start">
                <div className="flex items-center gap-4">
                  <div className="h-16 w-16 bg-primary/10 rounded-full flex items-center justify-center">
                    <User className="h-8 w-8 text-primary" />
                  </div>
                  <div>
                    <CardTitle className="text-2xl">{profile.name}</CardTitle>
                    <CardDescription className="text-lg">{profile.email}</CardDescription>
                    {profile.rating && (
                      <div className="flex items-center gap-2 mt-2">
                        <Star className="h-4 w-4 text-yellow-500 fill-current" />
                        <span className="text-sm font-medium">{profile.rating}</span>
                        <span className="text-sm text-muted-foreground">
                          ({profile.totalSessions} sessions)
                        </span>
                      </div>
                    )}
                  </div>
                </div>
                <Button
                  onClick={() => setIsEditing(!isEditing)}
                  variant={isEditing ? "outline" : "default"}
                  disabled={loading}
                >
                  {isEditing ? (
                    <>Cancel</>
                  ) : (
                    <>
                      <Edit className="h-4 w-4 mr-2" />
                      Edit Profile
                    </>
                  )}
                </Button>
              </div>
            </CardHeader>
          </Card>

          {/* Bio Section */}
          <Card>
            <CardHeader>
              <CardTitle>About</CardTitle>
            </CardHeader>
            <CardContent>
              {isEditing ? (
                <Textarea
                  value={editForm.bio}
                  onChange={(e) => setEditForm({ ...editForm, bio: e.target.value })}
                  placeholder="Tell clients about your coaching approach and experience..."
                  rows={4}
                />
              ) : (
                <p className="text-foreground">{profile.bio}</p>
              )}
            </CardContent>
          </Card>

          {/* Professional Details */}
          <div className="grid md:grid-cols-2 gap-6">
            {/* Experience & Credentials */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Award className="h-5 w-5" />
                  Experience & Credentials
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label>Experience</Label>
                  {isEditing ? (
                    <Input
                      value={editForm.experience}
                      onChange={(e) => setEditForm({ ...editForm, experience: e.target.value })}
                      placeholder="e.g., 5+ years of professional coaching"
                    />
                  ) : (
                    <p className="text-sm text-foreground mt-1">{profile.experience}</p>
                  )}
                </div>
                
                <div>
                  <Label>Certifications</Label>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {profile.certifications.map((cert, index) => (
                      <Badge key={index} variant="secondary">
                        {cert}
                      </Badge>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Location & Availability */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Clock className="h-5 w-5" />
                  Location & Availability
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label>Location</Label>
                  {isEditing ? (
                    <Input
                      value={editForm.location}
                      onChange={(e) => setEditForm({ ...editForm, location: e.target.value })}
                      placeholder="e.g., San Francisco, CA"
                    />
                  ) : (
                    <p className="text-sm text-foreground mt-1 flex items-center gap-2">
                      <MapPin className="h-4 w-4" />
                      {profile.location}
                    </p>
                  )}
                </div>
                
                <div>
                  <Label>Availability</Label>
                  {isEditing ? (
                    <Input
                      value={editForm.availability}
                      onChange={(e) => setEditForm({ ...editForm, availability: e.target.value })}
                      placeholder="e.g., Monday-Friday, 9 AM - 6 PM PST"
                    />
                  ) : (
                    <p className="text-sm text-foreground mt-1">{profile.availability}</p>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Specialties */}
          <Card>
            <CardHeader>
              <CardTitle>Specialties</CardTitle>
              <CardDescription>
                Areas of expertise and coaching focus
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {(isEditing ? editForm.specialties : profile.specialties).map((specialty, index) => (
                  <Badge 
                    key={index} 
                    variant="outline"
                    className={isEditing ? "cursor-pointer hover:bg-destructive hover:text-destructive-foreground" : ""}
                    onClick={isEditing ? () => removeSpecialty(specialty) : undefined}
                  >
                    {specialty}
                    {isEditing && <span className="ml-1">×</span>}
                  </Badge>
                ))}
              </div>
              {isEditing && (
                <div className="mt-4">
                  <Input
                    placeholder="Add a specialty and press Enter"
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') {
                        addSpecialty(e.currentTarget.value);
                        e.currentTarget.value = '';
                      }
                    }}
                  />
                </div>
              )}
            </CardContent>
          </Card>

          {/* Pricing */}
          <Card>
            <CardHeader>
              <CardTitle>Pricing</CardTitle>
            </CardHeader>
            <CardContent>
              <div>
                <Label>Hourly Rate</Label>
                {isEditing ? (
                  <Input
                    value={editForm.hourlyRate}
                    onChange={(e) => setEditForm({ ...editForm, hourlyRate: e.target.value })}
                    placeholder="e.g., $150"
                  />
                ) : (
                  <p className="text-lg font-semibold text-foreground mt-1">{profile.hourlyRate}</p>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Save/Cancel Actions */}
          {isEditing && (
            <div className="flex gap-4 justify-end">
              <Button variant="outline" onClick={handleCancel} disabled={loading}>
                Cancel
              </Button>
              <Button onClick={handleSave} disabled={loading}>
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Saving...
                  </>
                ) : (
                  <>
                    <Save className="h-4 w-4 mr-2" />
                    Save Changes
                  </>
                )}
              </Button>
            </div>
          )}
        </div>
      </div>
    </AppLayout>
  );
}