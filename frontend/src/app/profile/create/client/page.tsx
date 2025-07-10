"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";

interface ClientFormData {
  background: string;
  challenges: string[];
}

export default function ClientProfilePage() {
  const router = useRouter();
  const { user } = useAuth();
  const [formData, setFormData] = useState<ClientFormData>({
    background: "",
    challenges: [],
  });
  const [challengeInput, setChallengeInput] = useState("");

  const handleAddChallenge = () => {
    if (challengeInput.trim() && !formData.challenges.includes(challengeInput.trim())) {
      setFormData(prev => ({
        ...prev,
        challenges: [...prev.challenges, challengeInput.trim()]
      }));
      setChallengeInput("");
    }
  };

  const handleRemoveChallenge = (challenge: string) => {
    setFormData(prev => ({
      ...prev,
      challenges: prev.challenges.filter(c => c !== challenge)
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: Submit form data to backend
    console.log("Client profile data:", formData);
    // For now, redirect to a success page or dashboard
    router.push("/profile/edit");
  };

  return (
    <div className="min-h-screen bg-background py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-2xl mx-auto">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-extrabold text-foreground">
            Complete Your Client Profile
          </h2>
          <p className="mt-2 text-sm text-muted-foreground">
            Help us understand your background and what you're looking to achieve
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Client Information</CardTitle>
            <CardDescription>
              This information will help us match you with the right coach
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Background */}
              <div className="space-y-2">
                <Label htmlFor="background">Background</Label>
                <Textarea
                  id="background"
                  placeholder="Tell us about your background, current situation, and what brings you to coaching..."
                  value={formData.background}
                  onChange={(e) => setFormData(prev => ({
                    ...prev,
                    background: e.target.value
                  }))}
                  rows={4}
                  required
                />
              </div>

              {/* Challenges */}
              <div className="space-y-2">
                <Label htmlFor="challenges">Challenges & Goals</Label>
                <div className="flex gap-2">
                  <Input
                    id="challenges"
                    type="text"
                    placeholder="Add a challenge or goal (e.g., Career transition, Work-life balance)"
                    value={challengeInput}
                    onChange={(e) => setChallengeInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddChallenge())}
                  />
                  <Button type="button" onClick={handleAddChallenge} variant="outline">
                    Add
                  </Button>
                </div>
                {formData.challenges.length > 0 && (
                  <div className="flex flex-wrap gap-2 mt-2">
                    {formData.challenges.map((challenge, index) => (
                      <span
                        key={index}
                        className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-green-100 text-green-800"
                      >
                        {challenge}
                        <button
                          type="button"
                          onClick={() => handleRemoveChallenge(challenge)}
                          className="ml-2 text-green-600 hover:text-green-800"
                        >
                          ×
                        </button>
                      </span>
                    ))}
                  </div>
                )}
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