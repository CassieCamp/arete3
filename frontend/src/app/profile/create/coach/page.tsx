"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import { useAuth as useClerkAuth } from "@clerk/nextjs";

interface CoachFormData {
  first_name: string;
  last_name: string;
  coach_data: {
    specialties: string[];
    experience: number;
    philosophy: string;
  };
  organization: {
    name: string;
    description: string;
    website: string;
    industry: string;
    is_solo_practice: boolean;
  };
}

export default function CoachProfilePage() {
  const router = useRouter();
  const { user } = useAuth();
  const { getToken } = useClerkAuth();
  const [formData, setFormData] = useState<CoachFormData>({
    first_name: "",
    last_name: "",
    coach_data: {
      specialties: [],
      experience: 0,
      philosophy: "",
    },
    organization: {
      name: "",
      description: "",
      website: "",
      industry: "Professional Coaching",
      is_solo_practice: true,
    },
  });
  const [specialtyInput, setSpecialtyInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAddSpecialty = () => {
    if (specialtyInput.trim() && !formData.coach_data.specialties.includes(specialtyInput.trim())) {
      setFormData(prev => ({
        ...prev,
        coach_data: {
          ...prev.coach_data,
          specialties: [...prev.coach_data.specialties, specialtyInput.trim()]
        }
      }));
      setSpecialtyInput("");
    }
  };

  const handleRemoveSpecialty = (specialty: string) => {
    setFormData(prev => ({
      ...prev,
      coach_data: {
        ...prev.coach_data,
        specialties: prev.coach_data.specialties.filter(s => s !== specialty)
      }
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      const token = await getToken();
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/profiles/coach`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (response.ok) {
        // Profile created successfully
        console.log("Coach profile created:", data);
        router.push("/profile/edit");
      } else {
        setError(data.detail || "Failed to create profile. Please try again.");
      }
    } catch (err) {
      console.error("Profile creation error:", err);
      setError("Failed to create profile. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-2xl mx-auto">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-extrabold text-gray-900">
            Complete Your Coach Profile
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Tell us about your coaching experience and expertise
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Coach Information</CardTitle>
            <CardDescription>
              This information will help clients find and connect with you
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Specialties */}
              <div className="space-y-2">
                <Label htmlFor="specialties">Specialties</Label>
                <div className="flex gap-2">
                  <Input
                    id="specialties"
                    type="text"
                    placeholder="Add a specialty (e.g., Life Coaching, Career Development)"
                    value={specialtyInput}
                    onChange={(e) => setSpecialtyInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddSpecialty())}
                  />
                  <Button type="button" onClick={handleAddSpecialty} variant="outline">
                    Add
                  </Button>
                </div>
                {formData.coach_data.specialties.length > 0 && (
                  <div className="flex flex-wrap gap-2 mt-2">
                    {formData.coach_data.specialties.map((specialty, index) => (
                      <span
                        key={index}
                        className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-800"
                      >
                        {specialty}
                        <button
                          type="button"
                          onClick={() => handleRemoveSpecialty(specialty)}
                          className="ml-2 text-blue-600 hover:text-blue-800"
                        >
                          ×
                        </button>
                      </span>
                    ))}
                  </div>
                )}
              </div>

              {/* Experience */}
              <div className="space-y-2">
                <Label htmlFor="experience">Years of Experience</Label>
                <Input
                  id="experience"
                  type="number"
                  min="0"
                  placeholder="Enter years of coaching experience"
                  value={formData.coach_data.experience || ""}
                  onChange={(e) => setFormData(prev => ({
                    ...prev,
                    coach_data: {
                      ...prev.coach_data,
                      experience: parseInt(e.target.value) || 0
                    }
                  }))}
                  required
                />
              </div>

              {/* Philosophy */}
              <div className="space-y-2">
                <Label htmlFor="philosophy">Coaching Philosophy</Label>
                <Textarea
                  id="philosophy"
                  placeholder="Describe your coaching approach and philosophy..."
                  value={formData.coach_data.philosophy}
                  onChange={(e) => setFormData(prev => ({
                    ...prev,
                    coach_data: {
                      ...prev.coach_data,
                      philosophy: e.target.value
                    }
                  }))}
                  rows={4}
                  required
                />
              </div>

              {/* Organization Information */}
              <div className="space-y-4 border-t pt-6">
                <h3 className="text-lg font-medium text-gray-900">Organization Setup</h3>
                
                {/* Organization Name */}
                <div className="space-y-2">
                  <Label htmlFor="org-name">Organization/Practice Name</Label>
                  <Input
                    id="org-name"
                    type="text"
                    placeholder="Enter your coaching practice name"
                    value={formData.organization.name}
                    onChange={(e) => setFormData(prev => ({
                      ...prev,
                      organization: {
                        ...prev.organization,
                        name: e.target.value
                      }
                    }))}
                    required
                  />
                </div>

                {/* Organization Description */}
                <div className="space-y-2">
                  <Label htmlFor="org-description">Description</Label>
                  <Textarea
                    id="org-description"
                    placeholder="Describe your coaching practice..."
                    value={formData.organization.description}
                    onChange={(e) => setFormData(prev => ({
                      ...prev,
                      organization: {
                        ...prev.organization,
                        description: e.target.value
                      }
                    }))}
                    rows={3}
                  />
                </div>

                {/* Website */}
                <div className="space-y-2">
                  <Label htmlFor="org-website">Website (Optional)</Label>
                  <Input
                    id="org-website"
                    type="url"
                    placeholder="https://your-website.com"
                    value={formData.organization.website}
                    onChange={(e) => setFormData(prev => ({
                      ...prev,
                      organization: {
                        ...prev.organization,
                        website: e.target.value
                      }
                    }))}
                  />
                </div>

                {/* Solo Practice Toggle */}
                <div className="flex items-center space-x-2">
                  <input
                    id="solo-practice"
                    type="checkbox"
                    checked={formData.organization.is_solo_practice}
                    onChange={(e) => setFormData(prev => ({
                      ...prev,
                      organization: {
                        ...prev.organization,
                        is_solo_practice: e.target.checked
                      }
                    }))}
                    className="rounded border-gray-300"
                  />
                  <Label htmlFor="solo-practice">This is a solo practice</Label>
                </div>
              </div>

              {/* Personal Information */}
              <div className="space-y-4 border-t pt-6">
                <h3 className="text-lg font-medium text-gray-900">Personal Information</h3>
                
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="first-name">First Name</Label>
                    <Input
                      id="first-name"
                      type="text"
                      placeholder="Your first name"
                      value={formData.first_name}
                      onChange={(e) => setFormData(prev => ({
                        ...prev,
                        first_name: e.target.value
                      }))}
                      required
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="last-name">Last Name</Label>
                    <Input
                      id="last-name"
                      type="text"
                      placeholder="Your last name"
                      value={formData.last_name}
                      onChange={(e) => setFormData(prev => ({
                        ...prev,
                        last_name: e.target.value
                      }))}
                      required
                    />
                  </div>
                </div>
              </div>

              {error && (
                <div className="bg-red-50 border border-red-200 rounded-md p-4">
                  <p className="text-sm text-red-600">{error}</p>
                </div>
              )}

              <div className="flex gap-4">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => router.back()}
                  className="flex-1"
                >
                  Back
                </Button>
                <Button type="submit" className="flex-1" disabled={isLoading}>
                  {isLoading ? "Creating Profile..." : "Complete Profile"}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}