"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";

export default function RoleSelectionPage() {
  const router = useRouter();
  const { setUserRole } = useAuth();

  const handleRoleSelection = (role: 'coach' | 'client') => {
    setUserRole(role);
    router.push(`/profile/create/${role}`);
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
        
        <div className="space-y-4">
          <Card className="cursor-pointer hover:shadow-lg transition-shadow">
            <CardHeader>
              <CardTitle className="text-center">I'm a Coach</CardTitle>
              <CardDescription className="text-center">
                Help clients achieve their goals and share your expertise
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button 
                className="w-full" 
                onClick={() => handleRoleSelection('coach')}
                size="lg"
              >
                Continue as Coach
              </Button>
            </CardContent>
          </Card>

          <Card className="cursor-pointer hover:shadow-lg transition-shadow">
            <CardHeader>
              <CardTitle className="text-center">I'm a Client</CardTitle>
              <CardDescription className="text-center">
                Find the right coach and start your journey
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button 
                className="w-full" 
                variant="outline"
                onClick={() => handleRoleSelection('client')}
                size="lg"
              >
                Continue as Client
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}