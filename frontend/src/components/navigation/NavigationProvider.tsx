"use client";

import {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";
import { useUser, useAuth as useClerkAuth } from "@clerk/nextjs";
import {
  getMainNavigationForRole,
  getMenuNavigationForRole,
  MainNavigationItem,
  MenuNavigationItem,
} from "@/config/navigation";

interface NavigationContextType {
  mainNavigation: MainNavigationItem[];
  menuNavigation: MenuNavigationItem[];
  isMobileMenuOpen: boolean;
  setIsMobileMenuOpen: (open: boolean) => void;
  userRole: "member" | "coach" | "admin" | null;
  isLoading: boolean;
}

const NavigationContext = createContext<NavigationContextType | undefined>(
  undefined
);

interface NavigationProviderProps {
  children: ReactNode;
}

export function NavigationProvider({ children }: NavigationProviderProps) {
  const { user, isLoaded } = useUser();
  const { isSignedIn } = useClerkAuth();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [menuNavigation, setMenuNavigation] = useState<MenuNavigationItem[]>(
    []
  );
  const [mainNavigation, setMainNavigation] = useState<MainNavigationItem[]>(
    []
  );
  const [userRole, setUserRole] = useState<"member" | "coach" | "admin" | null>(
    null
  );
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (isLoaded) {
      if (isSignedIn && user) {
        // Get user role from Clerk's organization membership
        const orgMember =
          user.organizationMemberships && user.organizationMemberships[0];
        const primaryRole = orgMember ? orgMember.role : null;

        // Map Clerk roles to our navigation role system
        let navigationRole: "member" | "coach" | "admin";
        switch (primaryRole) {
          case "org:coach":
            navigationRole = "coach";
            break;
          case "org:admin":
            navigationRole = "admin";
            break;
          case "org:member":
          default:
            navigationRole = "member";
            break;
        }

        setUserRole(navigationRole);

        // Get navigation items directly for the user's role - no filtering needed!
        const roleMainNavigation = getMainNavigationForRole(navigationRole);
        const roleMenuNavigation = getMenuNavigationForRole(navigationRole);

        setMainNavigation(roleMainNavigation);
        setMenuNavigation(roleMenuNavigation);
        setIsLoading(false);
      } else {
        // User is not authenticated
        setUserRole(null);
        setMainNavigation([]);
        setMenuNavigation([]);
        setIsLoading(false);
      }
    }
  }, [user, isLoaded, isSignedIn]);

  const value: NavigationContextType = {
    mainNavigation,
    menuNavigation,
    isMobileMenuOpen,
    setIsMobileMenuOpen,
    userRole,
    isLoading,
  };

  return (
    <NavigationContext.Provider value={value}>
      {children}
    </NavigationContext.Provider>
  );
}

export function useNavigation() {
  const context = useContext(NavigationContext);
  if (context === undefined) {
    throw new Error("useNavigation must be used within a NavigationProvider");
  }
  return context;
}
