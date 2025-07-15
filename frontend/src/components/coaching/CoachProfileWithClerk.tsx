"use client";

import { useUser } from "@clerk/nextjs";
import { CoachProfile } from "./CoachProfile";
import { Skeleton } from "@/components/ui/skeleton";

interface CoachProfileWithClerkProps {
  userId: string;
}

export function CoachProfileWithClerk({ userId }: CoachProfileWithClerkProps) {
  const { user, isLoaded } = useUser({ id: userId });

  if (!isLoaded) {
    return <Skeleton className="w-full h-32" />;
  }

  if (!user) {
    return <div>Coach not found</div>;
  }

  const coach = {
    id: user.id,
    name: user.fullName || "Unnamed Coach",
    email: user.primaryEmailAddress?.emailAddress || "",
    imageUrl: user.imageUrl,
    // The following are placeholders as they are not available from the user object
    bio: "Coach bio coming soon.",
    specialties: ["Life Coaching", "Career Coaching"],
  };

  return <CoachProfile coach={coach} />;
}