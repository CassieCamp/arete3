import { LucideIcon } from 'lucide-react';
import { 
  Home, 
  Users, 
  FileText, 
  Target, 
  Brain,
  Settings,
  User,
  Calendar,
  BarChart3,
  MessageSquare
} from 'lucide-react';

export interface NavigationItem {
  id: string;
  title: string;
  href: string;
  icon: LucideIcon;
  description?: string;
  roles: ('coach' | 'client')[];
  badge?: string | number;
  children?: NavigationItem[];
  isExternal?: boolean;
}

export interface NavigationSection {
  id: string;
  title: string;
  items: NavigationItem[];
  roles: ('coach' | 'client')[];
}

export const NAVIGATION_CONFIG: NavigationSection[] = [
  {
    id: 'main',
    title: 'Main',
    roles: ['coach', 'client'],
    items: [
      {
        id: 'dashboard',
        title: 'Dashboard',
        href: '/dashboard',
        icon: Home,
        description: 'Overview and quick actions',
        roles: ['coach', 'client']
      },
      {
        id: 'connections',
        title: 'Connections',
        href: '/dashboard/connections',
        icon: Users,
        description: 'Manage coaching relationships',
        roles: ['coach', 'client']
      },
      {
        id: 'documents',
        title: 'Documents',
        href: '/dashboard/documents',
        icon: FileText,
        description: 'Upload and manage documents',
        roles: ['coach', 'client']
      },
      {
        id: 'goals',
        title: 'Goals',
        href: '/dashboard/goals',
        icon: Target,
        description: 'Track and manage goals',
        roles: ['coach', 'client']
      },
      {
        id: 'insights',
        title: 'Session Insights',
        href: '/dashboard/insights',
        icon: Brain,
        description: 'AI-powered session analysis',
        roles: ['coach', 'client']
      }
    ]
  },
  {
    id: 'coach-tools',
    title: 'Coach Tools',
    roles: ['coach'],
    items: [
      {
        id: 'client-overview',
        title: 'Client Overview',
        href: '/dashboard/clients',
        icon: BarChart3,
        description: 'Client progress and analytics',
        roles: ['coach']
      },
      {
        id: 'session-planning',
        title: 'Session Planning',
        href: '/dashboard/sessions',
        icon: Calendar,
        description: 'Plan and schedule sessions',
        roles: ['coach']
      },
      {
        id: 'coaching-notes',
        title: 'Coaching Notes',
        href: '/dashboard/notes',
        icon: MessageSquare,
        description: 'Session notes and observations',
        roles: ['coach']
      }
    ]
  },
  {
    id: 'account',
    title: 'Account',
    roles: ['coach', 'client'],
    items: [
      {
        id: 'profile',
        title: 'Profile',
        href: '/profile/edit',
        icon: User,
        description: 'Manage your profile',
        roles: ['coach', 'client']
      },
      {
        id: 'settings',
        title: 'Settings',
        href: '/dashboard/settings',
        icon: Settings,
        description: 'Account and preferences',
        roles: ['coach', 'client']
      }
    ]
  }
];

export function getNavigationForRole(role: 'coach' | 'client'): NavigationSection[] {
  return NAVIGATION_CONFIG
    .filter(section => section.roles.includes(role))
    .map(section => ({
      ...section,
      items: section.items.filter(item => item.roles.includes(role))
    }))
    .filter(section => section.items.length > 0);
}

export function getNavigationItem(id: string): NavigationItem | undefined {
  for (const section of NAVIGATION_CONFIG) {
    const item = section.items.find(item => item.id === id);
    if (item) return item;
  }
  return undefined;
}