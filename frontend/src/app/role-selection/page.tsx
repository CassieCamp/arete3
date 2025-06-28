"use client";

import { Button } from "@/components/ui/button";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import { useState } from "react";
import { useAuth as useClerkAuth } from "@clerk/nextjs";

export default function RoleSelectionPage() {
  const router = useRouter();
  const { setUserRole } = useAuth();
  const { getToken, userId } = useClerkAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleCoachSelection = async () => {
    if (!userId) {
      setError("Please sign in first");
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const token = await getToken();
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/users/access/check-coach-authorization`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      const data = await response.json();

      if (data.authorized) {
        setUserRole('coach');
        router.push('/profile/create/coach');
      } else {
        setError("You are not authorized to create a coach account. Please contact support if you believe this is an error.");
      }
    } catch (err) {
      setError("Failed to verify authorization. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleClientSelection = () => {
    setUserRole('client');
    router.push('/client-invitation');
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
            Choose Your Role
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Select whether you're joining as a coach or a client
          </p>
        </div>
        
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-md p-4">
            <p className="text-sm text-red-600">{error}</p>
          </div>
        )}
        
        <div className="space-y-4">
          <Button
            className="w-full bg-[#1B1E3C] hover:bg-[#1B1E3C]/90 !text-white"
            onClick={handleCoachSelection}
            size="lg"
            disabled={isLoading}
          >
            {isLoading ? "Checking Authorization..." : "Coach"}
          </Button>

          <Button
            className="w-full"
            variant="outline"
            onClick={handleClientSelection}
            size="lg"
            disabled={isLoading}
          >
            Client
          </Button>
        </div>
        
        <div className="text-center">
          <p className="text-xs text-gray-500">
            This is a beta version. Coach access is by invitation only.
            Clients must be invited by an authorized coach.
          </p>
        </div>
      </div>
    </div>
  );
}