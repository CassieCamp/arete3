"use client";

import React from 'react';
import { EnhancedHeader } from '@/components/layout/EnhancedHeader';
import { AuthProvider } from '@/context/AuthContext';

// Mock user data for testing header display
const mockUser = {
  id: 'test-user-123',
  firstName: 'Test',
  lastName: 'User',
  email: 'cassie@cassiecamp.com',
  primaryRole: 'admin' as const,
  organizationRoles: [
    {
      organizationId: 'org_mock_arete',
      organizationName: 'Arete Org',
      role: 'admin',
      orgType: 'arete' as const,
      permissions: ['platform:manage', 'users:manage', 'organizations:manage']
    },
    {
      organizationId: 'org_mock_coaching',
      organizationName: 'Morgan Liu Executive Coaching',
      role: 'coach',
      orgType: 'coach' as const,
      permissions: ['coaching_relationships:manage', 'client_data:read', 'resources:create']
    }
  ],
  permissions: ['platform:manage', 'users:manage', 'organizations:manage'],
  clerkId: 'test-clerk-123',
  role: 'coach' as const
};

// Mock AuthContext for testing
const MockAuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const mockAuthValue = {
    user: mockUser,
    isAuthenticated: true,
    roleLoaded: true,
    currentRole: 'admin',
    currentOrganization: 'org_mock_arete',
    login: () => {},
    logout: () => {},
    hasPermission: () => true,
    getAuthToken: async () => 'mock-token'
  };

  return (
    <div>
      {/* Simulate the auth context */}
      <div style={{ 
        position: 'fixed', 
        top: 0, 
        left: 0, 
        right: 0, 
        zIndex: 1000,
        background: 'white',
        borderBottom: '1px solid #e5e7eb'
      }}>
        <EnhancedHeader showRoleSwitcher={true} showNotifications={true} />
      </div>
      <div style={{ paddingTop: '60px' }}>
        {children}
      </div>
    </div>
  );
};

/**
 * Test page specifically for testing the header role and organization display
 */
export default function TestHeaderPage() {
  return (
    <MockAuthProvider>
      <div className="container mx-auto p-6 space-y-8">
        <div className="text-center space-y-4">
          <h1 className="text-4xl font-bold tracking-tight">Header Role & Organization Display Test</h1>
          <p className="text-lg text-muted-foreground max-w-3xl mx-auto">
            This page tests the enhanced header component with mock user data to verify that role and organization information displays correctly.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="p-6 bg-muted/30 rounded-lg border">
            <h3 className="text-lg font-semibold mb-4">Current Mock User Data</h3>
            <div className="space-y-2 text-sm">
              <div><strong>Name:</strong> {mockUser.firstName} {mockUser.lastName}</div>
              <div><strong>Email:</strong> {mockUser.email}</div>
              <div><strong>Primary Role:</strong> {mockUser.primaryRole}</div>
              <div><strong>Current Role:</strong> admin</div>
              <div><strong>Current Organization:</strong> Arete Org</div>
            </div>
          </div>

          <div className="p-6 bg-muted/30 rounded-lg border">
            <h3 className="text-lg font-semibold mb-4">Expected Header Display</h3>
            <div className="space-y-2 text-sm">
              <div>✓ Should show "Admin" badge</div>
              <div>✓ Should show "@Arete Org" organization name</div>
              <div>✓ Should display role switcher</div>
              <div>✓ Should show notifications bell</div>
              <div>✓ Should show settings menu</div>
              <div>✓ Should show user button</div>
            </div>
          </div>
        </div>

        <div className="p-6 bg-blue-50 border border-blue-200 rounded-lg">
          <h3 className="text-lg font-semibold text-blue-900 mb-2">Testing Instructions</h3>
          <p className="text-blue-700 text-sm">
            Look at the header above to verify that it displays:
            <br />• A badge showing "Admin" 
            <br />• Text showing "@Arete Org" next to the role badge
            <br />• All other header elements (role switcher, notifications, settings, user button)
          </p>
        </div>
      </div>
    </MockAuthProvider>
  );
}