import React from 'react';
import { useAuth } from '@/context/AuthContext';
import { getNavigationForUser, getMenuNavigationForUser, MainNavigationItem, MenuNavigationItem } from '@/config/navigation';
import { RoleGuard } from '@/components/auth';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import Link from 'next/link';

interface ContextAwareNavigationProps {
  variant?: 'main' | 'menu';
  className?: string;
  showRoleIndicator?: boolean;
}

/**
 * ContextAwareNavigation component that filters navigation items based on
 * the user's current role and permissions
 */
export const ContextAwareNavigation: React.FC<ContextAwareNavigationProps> = ({
  variant = 'main',
  className = '',
  showRoleIndicator = false
}) => {
  const { user, currentRole } = useAuth();

  if (!user) {
    return null;
  }

  // Get user roles and permissions
  const userRoles = [
    user.primaryRole,
    ...(user.organizationRoles?.map(orgRole => orgRole.role) || [])
  ];
  const userPermissions = user.permissions || [];
  const legacyRole = user.role; // For backward compatibility

  // Filter navigation items based on user's roles and permissions
  const navigationItems = variant === 'main' 
    ? getNavigationForUser(userRoles, userPermissions, legacyRole)
    : getMenuNavigationForUser(userRoles, userPermissions, legacyRole);

  if (navigationItems.length === 0) {
    return null;
  }

  return (
    <nav className={`context-aware-navigation ${className}`}>
      {showRoleIndicator && currentRole && (
        <div className="mb-4 flex items-center gap-2">
          <span className="text-sm text-muted-foreground">Current Role:</span>
          <Badge variant="outline" className="text-xs">
            {currentRole.charAt(0).toUpperCase() + currentRole.slice(1)}
          </Badge>
        </div>
      )}
      
      <div className={`navigation-items ${variant === 'main' ? 'grid grid-cols-1 gap-4' : 'flex flex-col gap-2'}`}>
        {navigationItems.map((item) => (
          <NavigationItem
            key={item.id}
            item={item}
            variant={variant}
            userRoles={userRoles}
            userPermissions={userPermissions}
          />
        ))}
      </div>
    </nav>
  );
};

interface NavigationItemProps {
  item: MainNavigationItem | MenuNavigationItem;
  variant: 'main' | 'menu';
  userRoles: string[];
  userPermissions: string[];
}

/**
 * Individual navigation item component with role-based access control
 */
const NavigationItem: React.FC<NavigationItemProps> = ({
  item,
  variant,
  userRoles,
  userPermissions
}) => {
  const { user } = useAuth();
  
  // Double-check access (redundant but safe)
  const hasAccess = () => {
    const hasRole = item.roles.some(role => userRoles.includes(role));
    const hasPermission = !item.permissions || 
      item.permissions.some(permission => userPermissions.includes(permission));
    const hasLegacyRole = user?.role && item.legacyRoles ? 
      item.legacyRoles.includes(user.role) : false;
    
    return (hasRole && hasPermission) || hasLegacyRole;
  };

  if (!hasAccess()) {
    return null;
  }

  const IconComponent = item.icon;

  if (variant === 'main') {
    const mainItem = item as MainNavigationItem;
    return (
      <RoleGuard
        requiredRoles={item.roles}
        requiredPermissions={item.permissions}
        fallback={null}
      >
        <Link href={mainItem.href || '#'} className="block">
          <div className="p-4 rounded-lg border border-border hover:bg-accent hover:text-accent-foreground transition-colors cursor-pointer">
            <div className="flex items-center gap-3">
              <IconComponent className="w-6 h-6" />
              <div className="flex-1">
                <h3 className="font-medium">{mainItem.label}</h3>
                <p className="text-sm text-muted-foreground">{mainItem.description}</p>
              </div>
            </div>
          </div>
        </Link>
      </RoleGuard>
    );
  }

  // Menu variant
  const menuItem = item as MenuNavigationItem;
  return (
    <RoleGuard
      requiredRoles={item.roles}
      requiredPermissions={item.permissions}
      fallback={null}
    >
      <Link href={menuItem.href} className="block">
        <Button
          variant="ghost"
          className="w-full justify-start gap-3 h-auto py-2"
        >
          <IconComponent className="w-4 h-4" />
          <span>{menuItem.label}</span>
        </Button>
      </Link>
    </RoleGuard>
  );
};

/**
 * Hook for getting filtered navigation items
 */
export const useContextAwareNavigation = () => {
  const { user } = useAuth();

  const getFilteredNavigation = (variant: 'main' | 'menu' = 'main') => {
    if (!user) return [];

    const userRoles = [
      user.primaryRole,
      ...(user.organizationRoles?.map(orgRole => orgRole.role) || [])
    ];
    const userPermissions = user.permissions || [];
    const legacyRole = user.role;

    return variant === 'main' 
      ? getNavigationForUser(userRoles, userPermissions, legacyRole)
      : getMenuNavigationForUser(userRoles, userPermissions, legacyRole);
  };

  return {
    getFilteredNavigation,
    hasNavigationAccess: (itemId: string, variant: 'main' | 'menu' = 'main') => {
      const items = getFilteredNavigation(variant);
      return items.some(item => item.id === itemId);
    }
  };
};

/**
 * Simple navigation wrapper that shows/hides based on permissions
 */
interface ConditionalNavigationProps {
  children: React.ReactNode;
  requiredRole?: string;
  requiredPermission?: string;
  requiredRoles?: string[];
  requiredPermissions?: string[];
  fallback?: React.ReactNode;
}

export const ConditionalNavigation: React.FC<ConditionalNavigationProps> = ({
  children,
  requiredRole,
  requiredPermission,
  requiredRoles,
  requiredPermissions,
  fallback = null
}) => {
  return (
    <RoleGuard
      requiredRole={requiredRole}
      requiredPermission={requiredPermission}
      requiredRoles={requiredRoles}
      requiredPermissions={requiredPermissions}
      fallback={fallback}
    >
      {children}
    </RoleGuard>
  );
};