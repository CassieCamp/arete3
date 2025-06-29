"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";

export default function ProfileEditPage() {
  const router = useRouter();
  const { user } = useAuth();

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-2xl mx-auto">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-extrabold text-gray-900">
            Profile Editing Page
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            This page will allow users to edit their profile information
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Profile Management</CardTitle>
            <CardDescription>
              Edit and update your profile information
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="text-center py-8">
              <p className="text-lg text-gray-600 mb-4">
                Profile editing functionality will be implemented in a future sprint.
              </p>
              {user && (
                <div className="bg-gray-100 p-4 rounded-lg mb-4">
                  <p className="text-sm text-gray-700">
                    <strong>Current User:</strong> {user.firstName} {user.lastName}
                  </p>
                  <p className="text-sm text-gray-700">
                    <strong>Email:</strong> {user.email}
                  </p>
                  {user.role && (
                    <p className="text-sm text-gray-700">
                      <strong>Role:</strong> {user.role}
                    </p>
                  )}
                </div>
              )}
            </div>
            
            <div className="flex gap-4">
              <Button
                variant="outline"
                onClick={() => router.push("/dashboard/connections")}
                className="flex-1"
              >
                Back to Dashboard
              </Button>
              <Button
                onClick={() => router.push("/")}
                className="flex-1"
              >
                Go to Home
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}