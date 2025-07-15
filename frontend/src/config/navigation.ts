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

// NOTE: Navigation arrays are role-specific by design to prevent accidental leakage of UI elements between roles.
// Do not co-locate role navigation or use shared arrays with runtime filtering.

// Main navigation items interface
export interface MainNavigationItem {
  id: 'microphone' | 'compass' | 'console' | 'practice' | 'clients' | 'organizations' | 'journey' | 'profile';
  icon: LucideIcon;
  label: string;
  description: string;
  href?: string;
  action?: string;
  permissions?: string[]; // Optional permissions for granular access control
}

// Menu items for the hamburger menu
export interface MenuNavigationItem {
  id: string;
  icon: LucideIcon;
  label: string;
  href: string;
  permissions?: string[]; // Optional permissions for granular access control
}

// ===== MEMBER NAVIGATION =====
// Navigation items specifically for users with primary_role: 'member'
export const MEMBER_NAVIGATION: MainNavigationItem[] = [
  {
    id: 'journey',
    icon: Route,
    label: 'Journey',
    description: 'Your timeline of growth and discovery',
    href: '/member/journey',
    permissions: ['profile:read']
  },
  {
    id: 'basecamp',
    icon: CaveIcon as any,
    label: 'Center',
    description: 'Your foundation and starting point',
    href: '/member/center',
    permissions: ['profile:read']
  },
  {
    id: 'compass',
    icon: Users,
    label: 'Coaching',
    description: 'Your coaching connections and relationships',
    href: '/member/coaching',
    permissions: ['profile:read']
  }
];

// ===== COACH NAVIGATION =====
// Navigation items specifically for users with primary_role: 'coach'
export const COACH_NAVIGATION: MainNavigationItem[] = [
  {
    id: 'practice',
    icon: PracticeIcon as any,
    label: 'Practice',
    description: 'Your coaching practice and tools',
    href: '/coach/practice'
  },
  {
    id: 'clients',
    icon: RippleIcon as any,
    label: 'Clients',
    description: 'Manage your coaching relationships',
    href: '/coach/clients',
    permissions: ['coaching_relationships:manage']
  },
  {
    id: 'profile',
    icon: CoachIcon as any,
    label: 'Profile',
    description: 'Your profile and settings',
    href: '/coach/profile',
    permissions: ['profile:manage']
  }
];

// ===== ADMIN NAVIGATION =====
// Navigation items specifically for users with primary_role: 'admin'
export const ADMIN_NAVIGATION: MainNavigationItem[] = [
  {
    id: 'organizations',
    icon: Building,
    label: 'Organizations',
    description: 'Manage organizations and memberships',
    href: '/organizations',
    permissions: ['organizations:manage']
  }
];

// ===== LEGACY SUPPORT =====
// Maintained for backward compatibility - will be deprecated
export const MAIN_NAVIGATION: MainNavigationItem[] = [
  ...MEMBER_NAVIGATION,
  ...COACH_NAVIGATION,
  ...ADMIN_NAVIGATION
];

// ===== MENU NAVIGATION (Role-Specific) =====

// Menu navigation for members
export const MEMBER_MENU_NAVIGATION: MenuNavigationItem[] = [
  {
    id: 'settings',
    icon: Settings,
    label: 'Settings',
    href: '/settings',
    permissions: ['profile:read']
  }
];

// Menu navigation for coaches
export const COACH_MENU_NAVIGATION: MenuNavigationItem[] = [
  {
    id: 'profile',
    icon: User,
    label: 'Profile',
    href: '/profile/edit',
    permissions: ['profile:manage']
  },
  {
    id: 'settings',
    icon: Settings,
    label: 'Settings',
    href: '/settings',
    permissions: ['profile:read']
  }
];

// Menu navigation for admins
export const ADMIN_MENU_NAVIGATION: MenuNavigationItem[] = [
  {
    id: 'profile',
    icon: User,
    label: 'Profile',
    href: '/profile/edit',
    permissions: ['profile:manage']
  },
  {
    id: 'settings',
    icon: Settings,
    label: 'Settings',
    href: '/settings',
    permissions: ['profile:read']
  }
];

// Legacy support - maintained for backward compatibility
export const MENU_NAVIGATION: MenuNavigationItem[] = [
  ...MEMBER_MENU_NAVIGATION,
  ...COACH_MENU_NAVIGATION,
  ...ADMIN_MENU_NAVIGATION
];

// ===== ROLE-BASED NAVIGATION GETTERS =====

/**
 * Get main navigation items for a specific role
 * This is the new preferred way to get navigation - direct role mapping
 */
export function getMainNavigationForRole(role: 'member' | 'coach' | 'admin'): MainNavigationItem[] {
  switch (role) {
    case 'member':
      return MEMBER_NAVIGATION;
    case 'coach':
      return COACH_NAVIGATION;
    case 'admin':
      return ADMIN_NAVIGATION;
    default:
      return [];
  }
}

/**
 * Get menu navigation items for a specific role
 * This is the new preferred way to get menu navigation - direct role mapping
 */
export function getMenuNavigationForRole(role: 'member' | 'coach' | 'admin'): MenuNavigationItem[] {
  switch (role) {
    case 'member':
      return MEMBER_MENU_NAVIGATION;
    case 'coach':
      return COACH_MENU_NAVIGATION;
    case 'admin':
      return ADMIN_MENU_NAVIGATION;
    default:
      return [];
  }
}

// ===== LEGACY SUPPORT FUNCTIONS =====
// These functions are maintained for backward compatibility but should be avoided in new code

/**
 * @deprecated Use getMainNavigationForRole instead
 * Legacy function for backward compatibility
 */
export function getNavigationForUser(
  userRoles: string[],
  userPermissions: string[],
  legacyRole?: 'coach' | 'client'
): MainNavigationItem[] {
  // Convert legacy role to new role system
  if (legacyRole === 'client') {
    return getMainNavigationForRole('member');
  } else if (legacyRole === 'coach') {
    return getMainNavigationForRole('coach');
  }
  
  // Fallback to member navigation
  return getMainNavigationForRole('member');
}

/**
 * @deprecated Use getMenuNavigationForRole instead
 * Legacy function for backward compatibility
 */
export function getMenuNavigationForUser(
  userRoles: string[],
  userPermissions: string[],
  legacyRole?: 'coach' | 'client'
): MenuNavigationItem[] {
  // Convert legacy role to new role system
  if (legacyRole === 'client') {
    return getMenuNavigationForRole('member');
  } else if (legacyRole === 'coach') {
    return getMenuNavigationForRole('coach');
  }
  
  // Fallback to member navigation
  return getMenuNavigationForRole('member');
}

// Helper function to get main navigation item by id
export function getMainNavigationItem(id: string): MainNavigationItem | undefined {
  return MAIN_NAVIGATION.find(item => item.id === id);
}

// Helper function to get menu navigation item by id
export function getMenuNavigationItem(id: string): MenuNavigationItem | undefined {
  return MENU_NAVIGATION.find(item => item.id === id);
}

/**
 * @deprecated Role-based access is now handled by direct role mapping
 * Helper function to check if user has access to a specific navigation item
 */
export function hasNavigationAccess(
  item: MainNavigationItem | MenuNavigationItem,
  userRoles: string[],
  userPermissions: string[],
  legacyRole?: 'coach' | 'client'
): boolean {
  // Check permission requirement (if specified)
  const hasPermission = !item.permissions ||
    item.permissions.some(permission => userPermissions.includes(permission));
  
  return hasPermission;
}