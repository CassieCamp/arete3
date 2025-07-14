import { LucideIcon } from 'lucide-react';
import {
  Route,
  Mic,
  User,
  Settings,
  BarChart3,
  Users,
  Building
} from 'lucide-react';
import { CaveIcon } from '@/components/icons/CaveIcon';
import { CoachIcon } from '@/components/icons/CoachIcon';
import { RippleIcon } from '@/components/icons/RippleIcon';
import { PracticeIcon } from '@/components/icons/PracticeIcon';

// Main navigation items for the enhanced role system
export interface MainNavigationItem {
  id: 'mountain' | 'microphone' | 'compass' | 'basecamp' | 'console' | 'practice' | 'clients' | 'organizations' | 'journey' | 'profile';
  icon: LucideIcon;
  label: string;
  description: string;
  href?: string;
  action?: string;
  roles: string[]; // Enhanced to support new role system
  permissions?: string[]; // Optional permissions for granular access control
  // Legacy support
  legacyRoles?: ('coach' | 'client')[];
}

// Menu items for the hamburger menu
export interface MenuNavigationItem {
  id: string;
  icon: LucideIcon;
  label: string;
  href: string;
  roles: string[]; // Enhanced to support new role system
  permissions?: string[]; // Optional permissions for granular access control
  // Legacy support
  legacyRoles?: ('coach' | 'client')[];
}

// Main navigation configuration
export const MAIN_NAVIGATION: MainNavigationItem[] = [
  {
    id: 'journey',
    icon: Route,
    label: 'Journey',
    description: 'Your timeline of growth and discovery',
    href: '/member/journey',
    roles: ['member'],
    permissions: ['profile:read'],
    legacyRoles: ['client']
  },
  {
    id: 'practice',
    icon: PracticeIcon as any,
    label: 'Practice',
    description: 'Your coaching practice and tools',
    href: '/coach/practice',
    roles: ['coach'],
    legacyRoles: ['coach']
  },
  {
    id: 'clients',
    icon: RippleIcon as any,
    label: 'Clients',
    description: 'Manage your coaching relationships',
    href: '/coach/clients',
    roles: ['coach'],
    permissions: ['coaching_relationships:manage'],
    legacyRoles: ['coach']
  },
  {
    id: 'basecamp',
    icon: CaveIcon as any,
    label: 'Center',
    description: 'Your foundation and starting point',
    href: '/member/center',
    roles: ['member'],
    permissions: ['profile:read'],
    legacyRoles: ['client']
  },
  {
    id: 'compass',
    icon: CoachIcon as any,
    label: 'Coaching',
    description: 'Your coaching connections and relationships',
    href: '/member/coaching',
    roles: ['member'],
    permissions: ['profile:read'],
    legacyRoles: ['client']
  },
  {
    id: 'profile',
    icon: CoachIcon as any,
    label: 'Profile',
    description: 'Your profile and settings',
    href: '/coach/profile',
    roles: ['member', 'coach'],
    permissions: ['profile:manage'],
    legacyRoles: ['client', 'coach']
  },
  {
    id: 'organizations',
    icon: Building,
    label: 'Organizations',
    description: 'Manage organizations and memberships',
    href: '/organizations',
    roles: ['admin'],
    permissions: ['organizations:manage']
  }
];

// Hamburger menu navigation configuration
export const MENU_NAVIGATION: MenuNavigationItem[] = [
  {
    id: 'profile',
    icon: User,
    label: 'Profile',
    href: '/profile/edit',
    roles: ['coach', 'member'],
    permissions: ['profile:manage'],
    legacyRoles: ['coach', 'client']
  },
  {
    id: 'settings',
    icon: Settings,
    label: 'Settings',
    href: '/settings',
    roles: ['coach', 'member'],
    permissions: ['profile:read'],
    legacyRoles: ['coach', 'client']
  }
];

// Enhanced helper function to filter navigation based on user roles and permissions
export function getNavigationForUser(
  userRoles: string[],
  userPermissions: string[],
  // Legacy support
  legacyRole?: 'coach' | 'client'
): MainNavigationItem[] {
  return MAIN_NAVIGATION.filter(item => {
    // Check new role system
    const hasRole = item.roles.some(role => userRoles.includes(role));
    
    // Check permission requirement (if specified)
    const hasPermission = !item.permissions ||
      item.permissions.some(permission => userPermissions.includes(permission));
    
    // Legacy support - fallback to old role system if new system doesn't match
    const hasLegacyRole = legacyRole && item.legacyRoles ?
      item.legacyRoles.includes(legacyRole) : false;
    
    return (hasRole && hasPermission) || hasLegacyRole;
  });
}

// Enhanced helper function to filter menu navigation
export function getMenuNavigationForUser(
  userRoles: string[],
  userPermissions: string[],
  // Legacy support
  legacyRole?: 'coach' | 'client'
): MenuNavigationItem[] {
  return MENU_NAVIGATION.filter(item => {
    // Check new role system
    const hasRole = item.roles.some(role => userRoles.includes(role));
    
    // Check permission requirement (if specified)
    const hasPermission = !item.permissions ||
      item.permissions.some(permission => userPermissions.includes(permission));
    
    // Legacy support - fallback to old role system if new system doesn't match
    const hasLegacyRole = legacyRole && item.legacyRoles ?
      item.legacyRoles.includes(legacyRole) : false;
    
    return (hasRole && hasPermission) || hasLegacyRole;
  });
}

// Legacy helper function for backward compatibility
export function getMenuNavigationForRole(role: 'coach' | 'client'): MenuNavigationItem[] {
  return MENU_NAVIGATION.filter(item =>
    item.legacyRoles?.includes(role) || item.roles.includes(role === 'client' ? 'member' : role)
  );
}

// Helper function to get main navigation item by id
export function getMainNavigationItem(id: string): MainNavigationItem | undefined {
  return MAIN_NAVIGATION.find(item => item.id === id);
}

// Helper function to get menu navigation item by id
export function getMenuNavigationItem(id: string): MenuNavigationItem | undefined {
  return MENU_NAVIGATION.find(item => item.id === id);
}

// Helper function to check if user has access to a specific navigation item
export function hasNavigationAccess(
  item: MainNavigationItem | MenuNavigationItem,
  userRoles: string[],
  userPermissions: string[],
  legacyRole?: 'coach' | 'client'
): boolean {
  // Check new role system
  const hasRole = item.roles.some(role => userRoles.includes(role));
  
  // Check permission requirement (if specified)
  const hasPermission = !item.permissions ||
    item.permissions.some(permission => userPermissions.includes(permission));
  
  // Legacy support
  const hasLegacyRole = legacyRole && item.legacyRoles ?
    item.legacyRoles.includes(legacyRole) : false;
  
  return (hasRole && hasPermission) || hasLegacyRole;
}