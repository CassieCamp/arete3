"use client";

import { useAuth } from "@/context/AuthContext";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function RoleBasedRedirect() {
  const { user, roleLoaded } = useAuth();
  const router = useRouter();

  useEffect(() => {
    console.log("RoleBasedRedirect - roleLoaded:", roleLoaded, "user:", user);
    if (roleLoaded) {
      console.log("Role is loaded, user role:", user?.primaryRole);
      if (user?.primaryRole === "coach") {
        console.log("Redirecting to coach dashboard");
        router.push("/coach/dashboard");
      } else {
        console.log("Redirecting to member journey");
        router.push("/member/journey");
      }
    }
  }, [user, roleLoaded, router]);

  if (!roleLoaded) {
    return <div>Loading your dashboard...</div>;
  }

  return null;
}