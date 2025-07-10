"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import { useState } from "react";
import { useAuth as useClerkAuth } from "@clerk/nextjs";

export default function ClientInvitationPage() {
  const router = useRouter();
  const { getToken, userId } = useClerkAuth();
  const [coachEmail, setCoachEmail] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!coachEmail.trim()) {
      setError("Please enter your coach's email address");
      return;
    }

    if (!userId) {
      setError("Please sign in first");
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const token = await getToken();
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/users/access/verify-coach-for-client`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ coach_email: coachEmail.trim() }),
      });

      const data = await response.json();

      if (response.ok && data.valid) {
        // Coach verified successfully
        router.push('/profile/create/client');
      } else {
        // Handle error response
        const errorMessage = data.detail || data.message || "Coach verification failed. Please check the email address and try again.";
        setError(typeof errorMessage === 'string' ? errorMessage : JSON.stringify(errorMessage));
      }
    } catch (err) {
      console.error('Coach verification error:', err);
      setError("Failed to verify coach. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <h2 className="mt-6 text-3xl font-extrabold text-foreground">
            Client Invitation
          </h2>
          <p className="mt-2 text-sm text-muted-foreground">
            Enter your coach's email address to verify your invitation
          </p>
        </div>
        
        {error && (
          <div className="bg-destructive/10 border border-destructive/20 rounded-md p-4">
            <p className="text-sm text-destructive">{error}</p>
          </div>
        )}
        
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <Label htmlFor="coach-email">Coach's Email Address</Label>
            <Input
              id="coach-email"
              type="email"
              value={coachEmail}
              onChange={(e) => setCoachEmail(e.target.value)}
              placeholder="coach@example.com"
              required
              disabled={isLoading}
              className="mt-1"
            />
          </div>
          
          <Button
            type="submit"
            className="w-full bg-primary hover:bg-primary/90 !text-primary-foreground"
            size="lg"
            disabled={isLoading}
          >
            {isLoading ? "Verifying Coach..." : "Continue"}
          </Button>
        </form>
        
        <div className="text-center">
          <Button
            variant="ghost"
            onClick={() => router.back()}
            disabled={isLoading}
            className="text-sm text-muted-foreground hover:text-foreground"
          >
            ← Back
          </Button>
        </div>
        
        <div className="text-center">
          <p className="text-xs text-muted-foreground">
            Only clients invited by authorized coaches can create accounts.
            If you're having trouble, please contact your coach.
          </p>
        </div>
      </div>
    </div>
  );
}