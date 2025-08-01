"use client";

import React, { createContext, useContext, ReactNode, useMemo } from "react";
import {
  useAuth as useClerkAuth,
  useUser,
  useOrganization,
  useOrganizationList,
} from "@clerk/nextjs";

interface OrganizationRole {
  organizationId: string;
  organizationName: string;
  role: string;
  orgType: "coach" | "member" | "arete";
  permissions: string[];
}

interface User {
  id: string;
  firstName: string;
  lastName: string;
  email: string;
  primaryRole: "admin" | "coach" | "member" | "client";
  organizationRoles: OrganizationRole[];
  permissions: string[];
  clerkId: string;
  // Legacy support for existing code
  role?: "coach" | "client";
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  roleLoaded: boolean;
  currentRole: string | null;
  currentOrganization: string | null;
  organizationRoles: OrganizationRole[];
  login: (user: User) => void;
  logout: () => void;
  hasPermission: (permission: string) => boolean;
  getAuthToken: () => Promise<string | null>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  // Use Clerk hooks directly - these are reactive and handle their own state
  const { isSignedIn, getToken } = useClerkAuth();
  const { user: clerkUser, isLoaded: userLoaded } = useUser();
  const { organization } = useOrganization();
  const { userMemberships, isLoaded: membershipsLoaded } =
    useOrganizationList();

  // Compute derived values using useMemo to prevent unnecessary recalculations
  const [user, setUser] = React.useState<User | null>(null);
  const [profileLoaded, setProfileLoaded] = React.useState(false);

  React.useEffect(() => {
    const fetchUserProfile = async () => {
      if (isSignedIn && clerkUser && userLoaded) {
        console.log("AuthContext: Fetching user profile, membershipsLoaded:", membershipsLoaded, "userMemberships:", userMemberships);
        setProfileLoaded(false);
        const token = await getToken({ template: "default" });
        if (token) {
          try {
            const orgId = organization?.id;
            const headers: HeadersInit = {
              Authorization: `Bearer ${token}`,
            };
            if (orgId) {
              headers["X-Org-Id"] = orgId;
            }
            const response = await fetch("/api/v1/users/me/profile", {
              headers,
            });
            if (response.ok) {
              const profile = await response.json();
              const primaryRole = profile.coach_data ? "coach" : "client";
              console.log("USER IS LOGGED IN AS:", primaryRole);

              // Only use organization data if it's loaded, otherwise use empty array
              const organizationRoles: OrganizationRole[] =
                (membershipsLoaded && userMemberships?.data)
                  ? userMemberships.data.map((membership) => ({
                      organizationId: membership.organization.id,
                      organizationName: membership.organization.name,
                      role: membership.role,
                      orgType: "member", // Default for now - can be enhanced later
                      permissions: [], // Permissions can be derived from role and org type
                    }))
                  : [];

              setUser({
                id: clerkUser.id,
                firstName: profile.first_name,
                lastName: profile.last_name,
                email: clerkUser.emailAddresses[0]?.emailAddress || "",
                primaryRole,
                organizationRoles,
                permissions: [], // This can be enhanced later
                clerkId: clerkUser.id,
                role: primaryRole,
              });
              setProfileLoaded(true);
            } else {
              console.error("Failed to fetch profile, status:", response.status);
              setProfileLoaded(true);
            }
          } catch (error) {
            console.error("Failed to fetch user profile:", error);
            setProfileLoaded(true);
          }
        } else {
          setProfileLoaded(true);
        }
      } else if (!isSignedIn) {
        setUser(null);
        setProfileLoaded(true);
      }
    };

    fetchUserProfile();
  }, [isSignedIn, clerkUser, userLoaded, getToken]);

  // Compute current role and organization
  const currentRole = useMemo((): string | null => {
    if (!user) return null;

    if (organization && userMemberships?.data) {
      // User is in an organization context - use Clerk's data directly
      const membership = userMemberships.data.find(
        (m) => m.organization.id === organization.id
      );
      return membership?.role || user.primaryRole;
    }

    // User is in personal account context
    return user.primaryRole;
  }, [user, organization, userMemberships]);

  const currentOrganization = useMemo((): string | null => {
    return organization?.id || null;
  }, [organization]);

  // Check if role data is loaded
  const roleLoaded = useMemo(() => {
    return profileLoaded && (!!user || !isSignedIn);
  }, [profileLoaded, user, isSignedIn]);

  // Helper functions
  const hasPermission = (permission: string): boolean => {
    if (!user) return false;

    // If in organization context, check organization-specific permissions
    if (currentRole && currentOrganization && organization) {
      const orgRole = user.organizationRoles.find(
        (r) =>
          r.organizationId === currentOrganization && r.role === currentRole
      );
      return orgRole?.permissions.includes(permission) || false;
    }

    // Otherwise check personal account permissions
    return user.permissions.includes(permission);
  };

  const login = (userData: User) => {
    // This is handled by Clerk, but we can set additional data if needed
    console.log("Login called with:", userData);
  };

  const logout = () => {
    // This should be handled by Clerk's signOut
    console.log("Logout called - use Clerk signOut instead");
  };

  const getAuthToken = async (): Promise<string | null> => {
    if (!isSignedIn) return null;
    try {
      const token = await getToken({ template: "default" });
      console.log("Clerk JWT:", token);
      return token;
    } catch (error) {
      console.error("Failed to get auth token:", error);
      return null;
    }
  };

  // Debug logging only when values actually change
  React.useEffect(() => {
    if (process.env.NODE_ENV === "development") {
      console.log("🐛 DEBUG - AuthContext state:", {
        isSignedIn,
        userLoaded,
        membershipsLoaded,
        roleLoaded,
        userId: user?.id || null,
        primaryRole: user?.primaryRole || null,
        currentRole,
        currentOrganization,
        organizationCount: user?.organizationRoles.length || 0,
        timestamp: new Date().toISOString(),
      });
    }
    if (isSignedIn) {
      getAuthToken();
    }
  }, [
    isSignedIn,
    userLoaded,
    membershipsLoaded,
    roleLoaded,
    user?.id,
    user?.primaryRole,
    currentRole,
    currentOrganization,
    user?.organizationRoles.length,
  ]);

  const value: AuthContextType = {
    user,
    isAuthenticated: isSignedIn || false,
    roleLoaded,
    currentRole,
    currentOrganization,
    organizationRoles: user?.organizationRoles || [],
    login,
    logout,
    hasPermission,
    getAuthToken,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
