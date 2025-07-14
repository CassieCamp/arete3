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
  profilePhoto?: string;
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
            {coach.profilePhoto ? (
              <img
                src={coach.profilePhoto}
                alt={`${coach.name}'s profile`}
                className="w-16 h-16 rounded-full object-cover border-2 border-border"
              />
            ) : (
              <div className="w-16 h-16 rounded-full bg-muted flex items-center justify-center border-2 border-border">
                <User className="w-8 h-8 text-muted-foreground" />
              </div>
            )}
          </div>

          {/* Coach Info */}
          <div className="flex-1 min-w-0">
            <CardTitle className="text-xl font-serif text-foreground mb-1">
              {coach.name}
            </CardTitle>
            
            <div className="flex items-center gap-4 text-sm text-muted-foreground mb-2">
              {coach.location && (
                <div className="flex items-center gap-1">
                  <MapPin className="w-4 h-4" />
                  <span>{coach.location}</span>
                </div>
              )}
              
              {coach.rating && (
                <div className="flex items-center gap-1">
                  <Star className="w-4 h-4 fill-current text-accent" />
                  <span>{coach.rating.toFixed(1)}</span>
                </div>
              )}
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
      {coach.bio && (
        <CardContent>
          <p className="text-sm text-muted-foreground leading-relaxed">
            {coach.bio}
          </p>
        </CardContent>
      )}
    </Card>
  );
}