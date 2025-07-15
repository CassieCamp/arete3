"use client";

import { AppLayout } from "@/components/layout/AppLayout";
import { ThreeIconNav } from "@/components/navigation/ThreeIconNav";
import { PageHeader } from "@/components/ui/page-header";
import { UnconnectedState } from "@/components/coaching/UnconnectedState";
import { ConnectedState } from "@/components/coaching/ConnectedState";
import { Users, Loader2 } from "lucide-react";
import { useCoachingRelationships } from "@/hooks/useCoachingRelationships";
import { useSessionSettings } from "@/hooks/useSessionSettings";

export default function CoachingPage() {
  const {
    relationships,
    isLoading: relationshipsLoading,
    error: relationshipsError,
    hasActiveRelationships
  } = useCoachingRelationships();

  const {
    settings,
    isLoading: settingsLoading,
    error: settingsError,
    toggleAutoSendContext
  } = useSessionSettings();

  // Transform relationships to include session settings
  const relationshipsWithSettings = relationships.map(rel => ({
    ...rel,
    autoSendEnabled: settings.session_auto_send_context
  }));

  const handleAutoSendChange = async (relationshipId: string, enabled: boolean) => {
    try {
      await toggleAutoSendContext();
    } catch (error) {
      console.error('Failed to update session settings:', error);
    }
  };

  const isLoading = relationshipsLoading || settingsLoading;
  const hasError = relationshipsError || settingsError;

  return (
    <AppLayout suppressBottomNav={true}>
      <ThreeIconNav />
      <div className="container mx-auto px-4 py-8 md:pt-20 pb-20">
        <PageHeader
          icon={Users}
          title="Coaching"
          subtitle=""
        />
        
        <div className="mt-8">
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <div className="flex items-center gap-3 text-muted-foreground">
                <Loader2 className="w-5 h-5 animate-spin" />
                <span>Loading your coaching information...</span>
              </div>
            </div>
          ) : hasError ? (
            <div className="max-w-2xl mx-auto text-center py-12">
              <div className="space-y-4">
                <div className="p-4 bg-destructive/10 rounded-lg border border-destructive/20">
                  <h3 className="font-semibold text-destructive mb-2">
                    Unable to Load Coaching Information
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    {relationshipsError || settingsError}
                  </p>
                </div>
                <p className="text-sm text-muted-foreground">
                  Please try refreshing the page. If the problem persists, contact support.
                </p>
              </div>
            </div>
          ) : hasActiveRelationships() ? (
            <ConnectedState
              relationships={relationshipsWithSettings}
              onAutoSendChange={handleAutoSendChange}
            />
          ) : (
            <UnconnectedState />
          )}
        </div>
      </div>
    </AppLayout>
  );
}