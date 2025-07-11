import { LucideIcon } from 'lucide-react';
import {
  Route,
  Mic,
  User,
  Settings
} from 'lucide-react';
import { CaveIcon } from '@/components/icons/CaveIcon';
import { CoachIcon } from '@/components/icons/CoachIcon';

// Main navigation items for the four-icon system
export interface MainNavigationItem {
  id: 'mountain' | 'microphone' | 'compass' | 'basecamp';
  icon: LucideIcon;
  label: string;
  description: string;
  href?: string;
  action?: string;
}

// Menu items for the hamburger menu
export interface MenuNavigationItem {
  id: string;
  icon: LucideIcon;
  label: string;
  href: string;
  roles: ('coach' | 'client')[];
}

// Main navigation configuration
export const MAIN_NAVIGATION: MainNavigationItem[] = [
  {
    id: 'mountain',
    icon: Route,
    label: 'Journey',
    description: 'Your timeline of growth and discovery',
    href: '/journey'
  },
  {
    id: 'basecamp',
    icon: CaveIcon as any,
    label: 'Center',
    description: 'Your foundation and starting point',
    href: '/basecamp'
  },
  {
    id: 'compass',
    icon: CoachIcon as any,
    label: 'Coach',
    description: '',
    href: '/coach'
  }
];

// Hamburger menu navigation configuration
export const MENU_NAVIGATION: MenuNavigationItem[] = [
  {
    id: 'profile',
    icon: User,
    label: 'Profile',
    href: '/profile/edit',
    roles: ['coach', 'client']
  },
  {
    id: 'settings',
    icon: Settings,
    label: 'Settings',
    href: '/settings',
    roles: ['coach', 'client']
  }
];

// Helper function to get menu items for a specific role
export function getMenuNavigationForRole(role: 'coach' | 'client'): MenuNavigationItem[] {
  return MENU_NAVIGATION.filter(item => item.roles.includes(role));
}

// Helper function to get main navigation item by id
export function getMainNavigationItem(id: string): MainNavigationItem | undefined {
  return MAIN_NAVIGATION.find(item => item.id === id);
}

// Helper function to get menu navigation item by id
export function getMenuNavigationItem(id: string): MenuNavigationItem | undefined {
  return MENU_NAVIGATION.find(item => item.id === id);
}