import React from 'react';
import { useUser, useAuth as useClerkAuth } from '@clerk/nextjs';

interface RoleGuardProps {
  children: React.ReactNode;
  requiredRole?: string;
  requiredPermission?: string;
  requiredRoles?: string[];
  requiredPermissions?: string[];
  fallback?: React.ReactNode;
  requireAll?: boolean; // If true, user must have ALL specified roles/permissions
}

/**
 * RoleGuard component provides role-based and permission-based access control
 * 
 * @param children - Content to render if access is granted
 * @param requiredRole - Single role required for access
 * @param requiredPermission - Single permission required for access
 * @param requiredRoles - Array of roles (user needs at least one unless requireAll is true)
 * @param requiredPermissions - Array of permissions (user needs at least one unless requireAll is true)
 * @param fallback - Content to render if access is denied (default: null)
 * @param requireAll - If true, user must have ALL specified roles/permissions (default: false)
 */
export const RoleGuard: React.FC<RoleGuardProps> = ({
  children,
  requiredRole,
  requiredPermission,
  requiredRoles,
  requiredPermissions,
  fallback = null,
  requireAll = false
}) => {
  const { user, isLoaded } = useUser();
  const { isSignedIn } = useClerkAuth();

  // If user is not authenticated or data not loaded, deny access
  if (!isLoaded || !isSignedIn || !user) {
    return <>{fallback}</>;
  }

  // Get user roles from Clerk's publicMetadata
  const primaryRole = user.publicMetadata?.primary_role as string;
  const organizationRoles = (user.publicMetadata?.organization_roles as any[]) || [];
  
  // Create a comprehensive list of user roles
  const userRoles = [
    primaryRole,
    ...organizationRoles.map((orgRole: any) => orgRole.role)
  ].filter(Boolean);

  // Check single role requirement
  if (requiredRole) {
    const hasRole = userRoles.includes(requiredRole);
    
    if (!hasRole) {
      return <>{fallback}</>;
    }
  }

  // Check multiple roles requirement
  if (requiredRoles && requiredRoles.length > 0) {
    const hasRequiredRoles = requireAll
      ? requiredRoles.every(role => userRoles.includes(role))
      : requiredRoles.some(role => userRoles.includes(role));
    
    if (!hasRequiredRoles) {
      return <>{fallback}</>;
    }
  }

  // For permissions, we'll implement a basic check based on roles
  // This can be enhanced later with more granular permission system
  const hasPermission = (permission: string): boolean => {
    // Basic permission mapping based on roles
    if (primaryRole === 'admin') return true;
    if (primaryRole === 'coach' && permission.includes('coach')) return true;
    if (primaryRole === 'member' && permission.includes('profile')) return true;
    return false;
  };

  // Check single permission requirement
  if (requiredPermission && !hasPermission(requiredPermission)) {
    return <>{fallback}</>;
  }

  // Check multiple permissions requirement
  if (requiredPermissions && requiredPermissions.length > 0) {
    const hasRequiredPermissions = requireAll
      ? requiredPermissions.every(permission => hasPermission(permission))
      : requiredPermissions.some(permission => hasPermission(permission));
    
    if (!hasRequiredPermissions) {
      return <>{fallback}</>;
    }
  }

  // All checks passed, render children
  return <>{children}</>;
};

/**
 * Hook for checking role/permission access in components
 */
export const useRoleGuard = () => {
  const { user, isLoaded } = useUser();
  const { isSignedIn } = useClerkAuth();

  const checkAccess = (options: Omit<RoleGuardProps, 'children' | 'fallback'>) => {
    if (!isLoaded || !isSignedIn || !user) return false;

    const {
      requiredRole,
      requiredPermission,
      requiredRoles,
      requiredPermissions,
      requireAll = false
    } = options;

    // Get user roles from Clerk's publicMetadata
    const primaryRole = user.publicMetadata?.primary_role as string;
    const organizationRoles = (user.publicMetadata?.organization_roles as any[]) || [];
    
    // Create a comprehensive list of user roles
    const userRoles = [
      primaryRole,
      ...organizationRoles.map((orgRole: any) => orgRole.role)
    ].filter(Boolean);

    // Check single role requirement
    if (requiredRole) {
      const hasRole = userRoles.includes(requiredRole);
      
      if (!hasRole) return false;
    }

    // Check multiple roles requirement
    if (requiredRoles && requiredRoles.length > 0) {
      const hasRequiredRoles = requireAll
        ? requiredRoles.every(role => userRoles.includes(role))
        : requiredRoles.some(role => userRoles.includes(role));
      
      if (!hasRequiredRoles) return false;
    }

    // Basic permission check based on roles
    const hasPermission = (permission: string): boolean => {
      if (primaryRole === 'admin') return true;
      if (primaryRole === 'coach' && permission.includes('coach')) return true;
      if (primaryRole === 'member' && permission.includes('profile')) return true;
      return false;
    };

    // Check single permission requirement
    if (requiredPermission && !hasPermission(requiredPermission)) {
      return false;
    }

    // Check multiple permissions requirement
    if (requiredPermissions && requiredPermissions.length > 0) {
      const hasRequiredPermissions = requireAll
        ? requiredPermissions.every(permission => hasPermission(permission))
        : requiredPermissions.some(permission => hasPermission(permission));
      
      if (!hasRequiredPermissions) return false;
    }

    return true;
  };

  return { checkAccess };
};