import React from 'react';
import { useAuth } from '@/context/AuthContext';
import { RoleGuard } from '@/components/auth';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { UserButton, OrganizationSwitcher } from '@clerk/nextjs';
import { Bell, Settings, Menu } from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import Link from 'next/link';

// Clerk OrganizationSwitcher appearance configuration
const clerkAppearance = {
  variables: {
    colorPrimary: "hsl(var(--primary))",
    colorBackground: "hsl(var(--background))",
    colorText: "hsl(var(--foreground))",
    colorTextSecondary: "hsl(var(--muted-foreground))",
    borderRadius: "calc(var(--radius) - 2px)",
    colorInputBackground: "hsl(var(--input))",
    colorInputText: "hsl(var(--foreground))"
  },
  elements: {
    // Trigger button styling
    organizationSwitcherTrigger: "flex items-center gap-2 px-3 py-2 text-sm font-medium rounded-md border border-input bg-background hover:bg-accent hover:text-accent-foreground transition-colors",
    
    // Dropdown styling
    organizationSwitcherPopoverCard: "w-64 p-1 bg-popover border border-border rounded-md shadow-md",
    
    // Organization preview styling
    organizationPreview: "flex items-center gap-3 p-2 rounded-sm hover:bg-accent transition-colors",
    
    // Action buttons
    organizationSwitcherPopoverActionButton: "w-full justify-start p-2 text-sm font-medium rounded-sm hover:bg-accent transition-colors",
    
    // Role badges
    membershipRole: "inline-flex items-center px-2 py-1 text-xs font-medium rounded-full bg-secondary text-secondary-foreground"
  }
};

interface EnhancedHeaderProps {
  className?: string;
  showRoleSwitcher?: boolean;
  showNotifications?: boolean;
  onMenuToggle?: () => void;
}

/**
 * Enhanced header component with role switching and context-aware features
 */
export const EnhancedHeader: React.FC<EnhancedHeaderProps> = ({
  className = '',
  showRoleSwitcher = true,
  showNotifications = true,
  onMenuToggle
}) => {
  const { user, currentRole, currentOrganization, isAuthenticated } = useAuth();

  if (!isAuthenticated || !user) {
    return (
      <header className={`border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 ${className}`}>
        <div className="container flex h-14 items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/">
              <h1 className="text-lg font-semibold cursor-pointer hover:opacity-80 transition-opacity">Arete</h1>
            </Link>
          </div>
          <div className="flex items-center gap-2">
            {/* Auth components would go here */}
          </div>
        </div>
      </header>
    );
  }

  return (
    <header className={`border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 ${className}`}>
      <div className="container flex h-14 items-center justify-between">
        <div className="flex items-center gap-4">
          {onMenuToggle && (
            <Button
              variant="ghost"
              size="sm"
              onClick={onMenuToggle}
              className="md:hidden"
            >
              <Menu className="w-4 h-4" />
            </Button>
          )}
          <Link href="/">
            <h1 className="text-lg font-semibold cursor-pointer hover:opacity-80 transition-opacity">Arete</h1>
          </Link>
          
          {/* Current role and organization indicator */}
          {currentRole && (
            <div className="hidden sm:flex items-center gap-2">
              <Badge variant="outline" className="font-medium">
                {currentRole.charAt(0).toUpperCase() + currentRole.slice(1)}
              </Badge>
              {currentOrganization && user?.organizationRoles && (
                <span className="text-sm text-muted-foreground">
                  @{user.organizationRoles.find(org => org.organizationId === currentOrganization)?.organizationName || 'Unknown Org'}
                </span>
              )}
            </div>
          )}
        </div>

        <div className="flex items-center gap-2">
          {/* Organization Switcher */}
          {showRoleSwitcher && (
            <div className="hidden md:block">
              <OrganizationSwitcher
                appearance={clerkAppearance}
                afterSelectOrganizationUrl="/dashboard"
                createOrganizationMode="modal"
              />
            </div>
          )}

          {/* Notifications */}
          {showNotifications && (
            <RoleGuard
              requiredPermissions={['notifications:read']}
              fallback={null}
            >
              <Button variant="ghost" size="sm">
                <Bell className="w-4 h-4" />
              </Button>
            </RoleGuard>
          )}

          {/* Settings Menu */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="sm">
                <Settings className="w-4 h-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56">
              {/* Role-specific menu items */}
              <RoleGuard requiredRole="admin">
                <DropdownMenuItem>
                  <Link href="/admin/dashboard" className="w-full">
                    Admin Dashboard
                  </Link>
                </DropdownMenuItem>
                <div className="border-t border-border my-1" />
              </RoleGuard>

              <RoleGuard requiredRole="coach">
                <DropdownMenuItem>
                  <Link href="/coach/settings" className="w-full">
                    Coach Settings
                  </Link>
                </DropdownMenuItem>
              </RoleGuard>

              <RoleGuard requiredRole="member">
                <DropdownMenuItem>
                  <Link href="/profile/edit" className="w-full">
                    Profile Settings
                  </Link>
                </DropdownMenuItem>
              </RoleGuard>

              <div className="border-t border-border my-1" />

              {/* Mobile organization switcher */}
              <div className="md:hidden p-2">
                <div className="text-sm font-medium mb-2">Switch Organization:</div>
                <OrganizationSwitcher
                  appearance={{
                    ...clerkAppearance,
                    elements: {
                      ...clerkAppearance.elements,
                      organizationSwitcherPopoverCard: "w-screen max-w-sm mx-4",
                      organizationSwitcherTrigger: "flex items-center gap-2 px-2 py-1 text-sm"
                    }
                  }}
                  afterSelectOrganizationUrl="/dashboard"
                  createOrganizationMode="modal"
                />
              </div>

              <div className="border-t border-border my-1 md:hidden" />

              <DropdownMenuItem>
                <Link href="/settings" className="w-full">
                  General Settings
                </Link>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>

          {/* User Button */}
          <UserButton 
            appearance={{
              elements: {
                avatarBox: "w-8 h-8"
              }
            }}
          />
        </div>
      </div>
    </header>
  );
};

/**
 * Simple header variant for pages that don't need full functionality
 */
export const SimpleHeader: React.FC<{ title?: string; className?: string }> = ({
  title = 'Arete',
  className = ''
}) => {
  const { user, currentRole, currentOrganization } = useAuth();

  return (
    <header className={`border-b border-border bg-background ${className}`}>
      <div className="container flex h-14 items-center justify-between">
        <div className="flex items-center gap-4">
          <Link href="/">
            <h1 className="text-lg font-semibold cursor-pointer hover:opacity-80 transition-opacity">{title}</h1>
          </Link>
          {user && currentRole && (
            <div className="flex items-center gap-2">
              <Badge variant="outline" className="text-xs font-medium">
                {currentRole.charAt(0).toUpperCase() + currentRole.slice(1)}
              </Badge>
              {currentOrganization && user?.organizationRoles && (
                <span className="text-xs text-muted-foreground">
                  @{user.organizationRoles.find(org => org.organizationId === currentOrganization)?.organizationName || 'Unknown Org'}
                </span>
              )}
            </div>
          )}
        </div>
        
        {user && (
          <div className="flex items-center gap-2">
            <UserButton 
              appearance={{
                elements: {
                  avatarBox: "w-8 h-8"
                }
              }}
            />
          </div>
        )}
      </div>
    </header>
  );
};

/**
 * Hook for header state management
 */
export const useHeaderState = () => {
  const { user, currentRole, currentOrganization, hasPermission } = useAuth();

  const getHeaderConfig = () => {
    if (!user) {
      return {
        showRoleSwitcher: false,
        showNotifications: false,
        showAdminMenu: false
      };
    }

    return {
      showRoleSwitcher: user.organizationRoles.length > 1 || (user.organizationRoles.length >= 1 && user.primaryRole),
      showNotifications: hasPermission('notifications:read'),
      showAdminMenu: hasPermission('admin:access') || currentRole === 'admin'
    };
  };

  return {
    headerConfig: getHeaderConfig(),
    currentRole,
    currentOrganization,
    user
  };
};