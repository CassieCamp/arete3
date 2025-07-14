"use client";

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useUser, useAuth as useClerkAuth } from '@clerk/nextjs';
import {
  MAIN_NAVIGATION,
  MENU_NAVIGATION,
  getMenuNavigationForRole,
  MainNavigationItem,
  MenuNavigationItem
} from '@/config/navigation';

interface NavigationContextType {
  mainNavigation: MainNavigationItem[];
  menuNavigation: MenuNavigationItem[];
  isMobileMenuOpen: boolean;
  setIsMobileMenuOpen: (open: boolean) => void;
  userRole: 'coach' | 'client' | null;
  isLoading: boolean;
}

const NavigationContext = createContext<NavigationContextType | undefined>(undefined);

interface NavigationProviderProps {
  children: ReactNode;
}

export function NavigationProvider({ children }: NavigationProviderProps) {
  const { user, isLoaded } = useUser();
  const { isSignedIn } = useClerkAuth();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [menuNavigation, setMenuNavigation] = useState<MenuNavigationItem[]>([]);
  const [mainNavigation, setMainNavigation] = useState<MainNavigationItem[]>([]);
  const [userRole, setUserRole] = useState<'coach' | 'client' | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (isLoaded) {
      if (isSignedIn && user) {
        // Get user role from Clerk's publicMetadata
        const primaryRole = user.publicMetadata?.primary_role as string;
        const role = primaryRole === 'coach' ? 'coach' : 'client'; // Convert to legacy format
        setUserRole(role);

        // Filter main navigation items based on role using the roles property
        const filteredMainNavigation = MAIN_NAVIGATION.filter(item => {
          return item.legacyRoles?.includes(role) || item.roles.includes(primaryRole);
        });
        setMainNavigation(filteredMainNavigation);

        // Get menu navigation items for the user's role
        const roleMenuNavigation = getMenuNavigationForRole(role);
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
    isLoading
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
    throw new Error('useNavigation must be used within a NavigationProvider');
  }
  return context;
}