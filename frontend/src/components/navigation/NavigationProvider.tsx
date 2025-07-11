"use client";

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useAuth } from '@/context/AuthContext';
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
  const { user, isAuthenticated, roleLoaded } = useAuth();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [menuNavigation, setMenuNavigation] = useState<MenuNavigationItem[]>([]);
  const [mainNavigation, setMainNavigation] = useState<MainNavigationItem[]>([]);
  const [userRole, setUserRole] = useState<'coach' | 'client' | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (isAuthenticated && user && roleLoaded) {
      // Determine user role from user object or profile
      const role = user.role as 'coach' | 'client' || 'client'; // Default to client
      setUserRole(role);
      
      // Filter main navigation items based on role using the roles property
      const filteredMainNavigation = MAIN_NAVIGATION.filter(item => {
        return item.roles.includes(role);
      });
      setMainNavigation(filteredMainNavigation);
      
      // Get menu navigation items for the user's role
      const roleMenuNavigation = getMenuNavigationForRole(role);
      setMenuNavigation(roleMenuNavigation);
      setIsLoading(false);
    } else if (isAuthenticated === false) {
      // User is not authenticated
      setIsLoading(false);
    } else if (!roleLoaded) {
      // Still loading role
      setIsLoading(true);
    }
  }, [user, isAuthenticated, roleLoaded]);

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