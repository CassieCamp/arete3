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
      <div className="text-center space-y-4">
        <div className="flex justify-center">
          <div className="p-4 bg-green-100 rounded-full">
            <CheckCircle className="w-12 h-12 text-green-600" />
          </div>
        </div>
        
        <div className="space-y-2">
          <h1 className="text-3xl font-bold text-foreground font-serif">
            Your Coaching Team
          </h1>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto leading-relaxed">
            You're connected with {relationships.length} {relationships.length === 1 ? 'coach' : 'coaches'}. 
            Manage your relationships and session preferences below.
          </p>
        </div>
      </div>

      {/* Coaches Section */}
      <div className="space-y-6">
        <div className="space-y-4">
          <h2 className="text-xl font-semibold text-foreground">
            Your {relationships.length === 1 ? 'Coach' : 'Coaches'}
          </h2>
          
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

      {/* Additional Info */}
      <div className="mt-12 p-6 bg-muted/30 rounded-lg border">
        <div className="space-y-3">
          <h3 className="font-semibold text-foreground">
            What's Next?
          </h3>
          <div className="space-y-2 text-sm text-muted-foreground">
            <p>
              • Your {relationships.length === 1 ? 'coach' : 'coaches'} will reach out to schedule your first session
            </p>
            <p>
              • Continue journaling and setting goals to get the most out of your coaching experience
            </p>
            <p>
              • Check your session preparation settings above to customize how you share context with your {relationships.length === 1 ? 'coach' : 'coaches'}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}