"use client";

import React from 'react';
import { useUser, useAuth, useOrganization } from '@clerk/nextjs';
import { OrganizationSwitcher } from '@clerk/nextjs';

/**
 * Test page for role-based functionality with Clerk OrganizationSwitcher
 */
export default function TestRolesPage() {
  const { user, isLoaded } = useUser();
  const { isSignedIn } = useAuth();
  const { organization } = useOrganization();

  // Get role information from Clerk's publicMetadata
  const primaryRole = user?.publicMetadata?.primary_role as string;
  const organizationRoles = (user?.publicMetadata?.organization_roles as any[]) || [];
  const currentRole = organization ?
    organizationRoles.find(orgRole => orgRole.organizationId === organization.id)?.role || primaryRole :
    primaryRole;
  const currentOrganization = organization?.id || null;

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-2xl font-bold mb-6">Role Testing with Clerk OrganizationSwitcher</h1>
      
      <div className="space-y-6">
        <div className="bg-card p-4 rounded-lg border">
          <h2 className="text-lg font-semibold mb-4">Current User Context</h2>
          <div className="space-y-2">
            <p><span className="font-medium">Current Role:</span> {currentRole || 'None'}</p>
            <p><span className="font-medium">Current Organization:</span> {currentOrganization || 'Personal Account'}</p>
            <p><span className="font-medium">User ID:</span> {user?.id || 'Not authenticated'}</p>
            <p><span className="font-medium">Primary Role:</span> {primaryRole || 'None'}</p>
            <p><span className="font-medium">Is Loaded:</span> {isLoaded ? 'Yes' : 'No'}</p>
            <p><span className="font-medium">Is Signed In:</span> {isSignedIn ? 'Yes' : 'No'}</p>
          </div>
        </div>

        <div className="bg-card p-4 rounded-lg border">
          <h2 className="text-lg font-semibold mb-4">Organization Switcher</h2>
          <OrganizationSwitcher 
            appearance={{
              variables: {
                colorPrimary: "hsl(var(--primary))",
                colorBackground: "hsl(var(--background))",
                colorText: "hsl(var(--foreground))",
              }
            }}
            afterSelectOrganizationUrl="/test-roles"
            createOrganizationMode="modal"
          />
        </div>

        <div className="bg-card p-4 rounded-lg border">
          <h2 className="text-lg font-semibold mb-4">Organization Roles</h2>
          {organizationRoles && organizationRoles.length > 0 ? (
            <ul className="space-y-2">
              {organizationRoles.map((orgRole, index) => (
                <li key={index} className="flex items-center gap-2">
                  <span className="font-medium">{orgRole.role}</span>
                  <span className="text-muted-foreground">@{orgRole.organizationName}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-muted-foreground">No organization roles found</p>
          )}
        </div>
      </div>
    </div>
  );
}