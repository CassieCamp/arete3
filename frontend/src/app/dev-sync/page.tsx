"use client";

import { Button } from "@/components/ui/button";
import { useAuth as useClerkAuth } from "@clerk/nextjs";
import { useState } from "react";

export default function DevSyncPage() {
  const { getToken, userId } = useClerkAuth();
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleSyncUser = async () => {
    if (!userId) {
      setResult({ error: "Please sign in first" });
      return;
    }

    setLoading(true);
    setResult(null);

    try {
      const token = await getToken();
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/users/dev/create-current-user`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      const data = await response.json();
      setResult(data);
    } catch (error) {
      setResult({ error: `Failed to sync user: ${error}` });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <h2 className="mt-6 text-3xl font-extrabold text-foreground">
            Development User Sync
          </h2>
          <p className="mt-2 text-sm text-muted-foreground">
            Sync your current Clerk user to the backend database
          </p>
        </div>
        
        <div className="space-y-4">
          <Button
            onClick={handleSyncUser}
            disabled={loading}
            className="w-full bg-primary hover:bg-primary/90 !text-primary-foreground"
            size="lg"
          >
            {loading ? "Syncing..." : "Sync Current User"}
          </Button>
          
          {result && (
            <div className={`p-4 rounded-md ${result.error ? 'bg-destructive/10 border border-destructive/20' : 'bg-secondary/10 border border-secondary/20'}`}>
              <pre className="text-sm whitespace-pre-wrap">
                {JSON.stringify(result, null, 2)}
              </pre>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}