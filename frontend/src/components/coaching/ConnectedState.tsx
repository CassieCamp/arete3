"use client";

import { CoachProfile } from "./CoachProfile";
import { SessionSettings } from "./SessionSettings";
import { CheckCircle } from "lucide-react";

interface Coach {
  id: string;
  name: string;
  email: string;
  bio?: string;
  specialties?: string[];
  location?: string;
  rating?: number;
  profilePhoto?: string;
}

interface CoachingRelationship {
  id: string;
  coach: Coach;
  status: string;
  createdAt: string;
  autoSendEnabled?: boolean;
}

interface ConnectedStateProps {
  relationships: CoachingRelationship[];
  onAutoSendChange?: (relationshipId: string, enabled: boolean) => void;
}

export function ConnectedState({ relationships, onAutoSendChange }: ConnectedStateProps) {
  const handleAutoSendChange = (relationshipId: string) => (enabled: boolean) => {
    onAutoSendChange?.(relationshipId, enabled);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header Section */}

      {/* Coaches Section */}
      <div className="space-y-6">
        <div className="space-y-4">
          
          <div className="grid gap-6">
            {relationships.map((relationship) => (
              <CoachProfile 
                key={relationship.id} 
                coach={relationship.coach} 
              />
            ))}
          </div>
        </div>
      </div>

      {/* Session Settings Section */}
      <div className="space-y-4">
        <h2 className="text-xl font-semibold text-foreground">
          Session Preferences
        </h2>
        
        <SessionSettings 
          autoSendEnabled={relationships[0]?.autoSendEnabled || false}
          onAutoSendChange={handleAutoSendChange(relationships[0]?.id || '')}
        />
      </div>

    </div>
  );
}