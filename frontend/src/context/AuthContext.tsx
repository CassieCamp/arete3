"use client";

import React, { createContext, useContext, useState, ReactNode } from 'react';
import { useAuth as useClerkAuth, useUser } from "@clerk/nextjs";

interface User {
  id: string;
  firstName: string;
  lastName: string;
  email: string;
  role?: 'coach' | 'client';
  clerkId?: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  roleLoaded: boolean;
  login: (user: User) => void;
  logout: () => void;
  getAuthToken: () => Promise<string | null>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const { isSignedIn, getToken } = useClerkAuth();
  const { user: clerkUser } = useUser();
  const [userRole, setUserRoleState] = useState<'coach' | 'client' | undefined>();
  const [roleLoaded, setRoleLoaded] = useState(false);

  // Fetch user role from backend when user is authenticated
  React.useEffect(() => {
    const fetchUserRole = async () => {
      console.log('🐛 DEBUG - AuthContext fetchUserRole:', {
        isSignedIn,
        hasClerkUser: !!clerkUser,
        roleLoaded,
        currentUserRole: userRole,
        timestamp: new Date().toISOString()
      });
      
      if (isSignedIn && clerkUser && !roleLoaded) {
        try {
          console.log('🐛 DEBUG - Fetching user role from backend...');
          const token = await getToken();
          if (token) {
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
            const response = await fetch(`${apiUrl}/api/v1/users/me`, {
              headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
              },
            });
            
            if (response.ok) {
              const userData = await response.json();
              console.log('🐛 DEBUG - Successfully fetched user data:', userData);
              setUserRoleState(userData.role);
              setRoleLoaded(true);
            } else {
              console.log('🐛 DEBUG - Failed to fetch user data, response not ok:', response.status);
            }
          } else {
            console.log('🐛 DEBUG - No token available');
          }
        } catch (error) {
          console.error('🐛 DEBUG - Failed to fetch user role:', error);
          setRoleLoaded(true); // Set to true even on error to prevent infinite loading
        }
      }
    };

    fetchUserRole();
  }, [isSignedIn, clerkUser, getToken, roleLoaded]);

  // Create user object from Clerk data
  const user: User | null = isSignedIn && clerkUser ? {
    id: clerkUser.id,
    firstName: clerkUser.firstName || '',
    lastName: clerkUser.lastName || '',
    email: clerkUser.emailAddresses[0]?.emailAddress || '',
    role: userRole,
    clerkId: clerkUser.id
  } : null;

  console.log('🐛 DEBUG - AuthContext user object:', {
    user,
    userRole,
    roleLoaded,
    timestamp: new Date().toISOString()
  });

  const login = (userData: User) => {
    // This is handled by Clerk, but we can set additional data if needed
    setUserRoleState(userData.role);
  };

  const logout = () => {
    // This should be handled by Clerk's signOut
    setUserRoleState(undefined);
  };


  const getAuthToken = async (): Promise<string | null> => {
    if (!isSignedIn) return null;
    try {
      return await getToken();
    } catch (error) {
      console.error('Failed to get auth token:', error);
      return null;
    }
  };

  const value: AuthContextType = {
    user,
    isAuthenticated: isSignedIn || false,
    roleLoaded,
    login,
    logout,
    getAuthToken,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};