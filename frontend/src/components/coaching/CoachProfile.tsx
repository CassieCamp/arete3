"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { User, MapPin, Star } from "lucide-react";

interface Coach {
  id: string;
  name: string;
  email: string;
  bio?: string;
  specialties?: string[];
  location?: string;
  rating?: number;
  imageUrl?: string;
}

interface CoachProfileProps {
  coach: Coach;
}

export function CoachProfile({ coach }: CoachProfileProps) {
  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex items-start gap-4">
          {/* Profile Photo */}
          <div className="flex-shrink-0">
            <img
              src="/images/yoda-jedi.png"
              alt={`${coach.name}'s profile`}
              className="w-24 h-24 rounded-full object-cover border-2 border-border"
            />
          </div>

          {/* Coach Info */}
          <div className="flex-1 min-w-0">
            <CardTitle className="text-xl font-serif text-foreground mb-1">
              Master Yoda
            </CardTitle>
            
            <div className="text-sm text-muted-foreground mb-2 space-y-1">
              <p><strong>Session Count:</strong> 6</p>
              <p><strong>First Session Date:</strong> 3 ABY, Month 2</p>
              <p><strong>Last Session Date:</strong> 4 ABY, Month 1</p>
            </div>

            {/* Specialties */}
            {coach.specialties && coach.specialties.length > 0 && (
              <div className="flex flex-wrap gap-2 mb-3">
                {coach.specialties.map((specialty, index) => (
                  <Badge 
                    key={index} 
                    variant="secondary"
                    className="text-xs"
                  >
                    {specialty}
                  </Badge>
                ))}
              </div>
            )}
          </div>
        </div>
      </CardHeader>

      {/* Bio */}
      <CardContent>
        <blockquote className="mt-6 border-l-2 pl-6 italic">
          "Remember this question, you must: 'What am I bringing with me?' Into every situation, ask this you should. Into every relationship, every decision, every moment of challenge - what fears, what anger, what assumptions do you carry?"
        </blockquote>
      </CardContent>
    </Card>
  );
}