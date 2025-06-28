"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";

interface CoachFormData {
  specialties: string[];
  experience: number;
  philosophy: string;
}

export default function CoachProfilePage() {
  const router = useRouter();
  const { user } = useAuth();
  const [formData, setFormData] = useState<CoachFormData>({
    specialties: [],
    experience: 0,
    philosophy: "",
  });
  const [specialtyInput, setSpecialtyInput] = useState("");

  const handleAddSpecialty = () => {
    if (specialtyInput.trim() && !formData.specialties.includes(specialtyInput.trim())) {
      setFormData(prev => ({
        ...prev,
        specialties: [...prev.specialties, specialtyInput.trim()]
      }));
      setSpecialtyInput("");
    }
  };

  const handleRemoveSpecialty = (specialty: string) => {
    setFormData(prev => ({
      ...prev,
      specialties: prev.specialties.filter(s => s !== specialty)
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: Submit form data to backend
    console.log("Coach profile data:", formData);
    // For now, redirect to a success page or dashboard
    router.push("/profile/edit");
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
                {formData.specialties.length > 0 && (
                  <div className="flex flex-wrap gap-2 mt-2">
                    {formData.specialties.map((specialty, index) => (
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
                  value={formData.experience || ""}
                  onChange={(e) => setFormData(prev => ({
                    ...prev,
                    experience: parseInt(e.target.value) || 0
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
                  value={formData.philosophy}
                  onChange={(e) => setFormData(prev => ({
                    ...prev,
                    philosophy: e.target.value
                  }))}
                  rows={4}
                  required
                />
              </div>

              <div className="flex gap-4">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => router.back()}
                  className="flex-1"
                >
                  Back
                </Button>
                <Button type="submit" className="flex-1">
                  Complete Profile
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}