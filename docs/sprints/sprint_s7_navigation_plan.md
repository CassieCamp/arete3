# Sprint S7: Unified Dashboard Navigation System - Technical Plan

## Sprint Goal

**"Create a unified, scalable, mobile-first navigation system for the entire dashboard area that provides role-based navigation with consistent UI patterns and responsive design."**

## Overview

This sprint introduces a comprehensive dashboard navigation system that replaces the current page-by-page layout approach with a unified layout component. The system features mobile-first responsive design, role-based navigation menus, and leverages the existing Arete UI component library for consistency.

## Architecture Overview

The navigation system follows established Arete patterns:

- **Layout Component**: [`DashboardLayout`](frontend/src/app/dashboard/layout.tsx) wraps all dashboard pages
- **Navigation Component**: [`DashboardNav`](frontend/src/components/navigation/DashboardNav.tsx) renders navigation links
- **Configuration System**: Centralized navigation configuration with role-based filtering
- **Responsive Design**: Mobile-first approach with sidebar/hamburger menu adaptation
- **UI Integration**: Uses existing [`Button`](frontend/src/components/ui/button.tsx), [`Card`](frontend/src/components/ui/card.tsx) components

## Navigation Architecture Diagram

```mermaid
graph TD
    A[Dashboard Layout] --> B[Navigation Provider]
    B --> C[Desktop Sidebar]
    B --> D[Mobile Hamburger Menu]
    C --> E[Navigation Items]
    D --> E
    E --> F[Role-Based Filtering]
    F --> G[Coach Navigation Items]
    F --> H[Client Navigation Items]
    
    I[Navigation Configuration] --> F
    J[User Context] --> F
    
    K[Dashboard Pages] --> A
    L[/dashboard/connections] --> K
    M[/dashboard/documents] --> K
    N[/dashboard/goals] --> K
    O[/dashboard/insights] --> K
```

## 1. Navigation Configuration System

### Navigation Configuration File

Create new file: [`frontend/src/config/navigation.ts`](frontend/src/config/navigation.ts)

```typescript
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
```

## 2. Dashboard Layout Component

### Main Layout Implementation

Create new file: [`frontend/src/app/dashboard/layout.tsx`](frontend/src/app/dashboard/layout.tsx)

```typescript
"use client";

import { ReactNode } from 'react';
import DashboardNav from '@/components/navigation/DashboardNav';
import { NavigationProvider } from '@/components/navigation/NavigationProvider';

interface DashboardLayoutProps {
  children: ReactNode;
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  return (
    <NavigationProvider>
      <div className="min-h-screen bg-background">
        {/* Navigation */}
        <DashboardNav />
        
        {/* Main Content */}
        <div className="lg:pl-64">
          <main className="py-6">
            <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
              {children}
            </div>
          </main>
        </div>
      </div>
    </NavigationProvider>
  );
}
```

## 3. Navigation Provider Context

### Navigation Context Implementation

Create new file: [`frontend/src/components/navigation/NavigationProvider.tsx`](frontend/src/components/navigation/NavigationProvider.tsx)

```typescript
"use client";

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useAuth } from '@/context/AuthContext';
import { getNavigationForRole, NavigationSection } from '@/config/navigation';

interface NavigationContextType {
  navigation: NavigationSection[];
  isMobileMenuOpen: boolean;
  setIsMobileMenuOpen: (open: boolean) => void;
  userRole: 'coach' | 'client' | null;
  isLoading: boolean;
}

const NavigationContext = createContext<NavigationContextType | undefined>(undefined);

interface NavigationProviderProps {
  children: ReactNode;
}

export function NavigationProvider({ children }: NavigationProviderProps) {
  const { user, isLoading: authLoading } = useAuth();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [navigation, setNavigation] = useState<NavigationSection[]>([]);
  const [userRole, setUserRole] = useState<'coach' | 'client' | null>(null);

  useEffect(() => {
    if (user && !authLoading) {
      // Determine user role from user object or profile
      const role = user.role as 'coach' | 'client' || 'client'; // Default to client
      setUserRole(role);
      
      // Get navigation items for the user's role
      const roleNavigation = getNavigationForRole(role);
      setNavigation(roleNavigation);
    }
  }, [user, authLoading]);

  const value: NavigationContextType = {
    navigation,
    isMobileMenuOpen,
    setIsMobileMenuOpen,
    userRole,
    isLoading: authLoading
  };

  return (
    <NavigationContext.Provider value={value}>
      {children}
    </NavigationContext.Provider>
  );
}

export function useNavigation() {
  const context = useContext(NavigationContext);
  if (context === undefined) {
    throw new Error('useNavigation must be used within a NavigationProvider');
  }
  return context;
}
```

## 4. Main Navigation Component

### DashboardNav Implementation

Create new file: [`frontend/src/components/navigation/DashboardNav.tsx`](frontend/src/components/navigation/DashboardNav.tsx)

```typescript
"use client";

import { Fragment } from 'react';
import { usePathname } from 'next/navigation';
import Link from 'next/link';
import { Dialog, Transition } from '@headlessui/react';
import { X, Menu, ChevronDown } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { useNavigation } from './NavigationProvider';
import { cn } from '@/lib/utils';

export default function DashboardNav() {
  const { navigation, isMobileMenuOpen, setIsMobileMenuOpen, userRole, isLoading } = useNavigation();
  const pathname = usePathname();

  if (isLoading) {
    return <NavigationSkeleton />;
  }

  return (
    <>
      {/* Mobile menu */}
      <Transition.Root show={isMobileMenuOpen} as={Fragment}>
        <Dialog as="div" className="relative z-50 lg:hidden" onClose={setIsMobileMenuOpen}>
          <Transition.Child
            as={Fragment}
            enter="transition-opacity ease-linear duration-300"
            enterFrom="opacity-0"
            enterTo="opacity-100"
            leave="transition-opacity ease-linear duration-300"
            leaveFrom="opacity-100"
            leaveTo="opacity-0"
          >
            <div className="fixed inset-0 bg-gray-900/80" />
          </Transition.Child>

          <div className="fixed inset-0 flex">
            <Transition.Child
              as={Fragment}
              enter="transition ease-in-out duration-300 transform"
              enterFrom="-translate-x-full"
              enterTo="translate-x-0"
              leave="transition ease-in-out duration-300 transform"
              leaveFrom="translate-x-0"
              leaveTo="-translate-x-full"
            >
              <Dialog.Panel className="relative mr-16 flex w-full max-w-xs flex-1">
                <Transition.Child
                  as={Fragment}
                  enter="ease-in-out duration-300"
                  enterFrom="opacity-0"
                  enterTo="opacity-100"
                  leave="ease-in-out duration-300"
                  leaveFrom="opacity-100"
                  leaveTo="opacity-0"
                >
                  <div className="absolute left-full top-0 flex w-16 justify-center pt-5">
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => setIsMobileMenuOpen(false)}
                      className="text-white hover:text-white hover:bg-white/10"
                    >
                      <X className="h-6 w-6" />
                    </Button>
                  </div>
                </Transition.Child>
                
                <div className="flex grow flex-col gap-y-5 overflow-y-auto bg-card px-6 pb-2 ring-1 ring-white/10">
                  <div className="flex h-16 shrink-0 items-center">
                    <div className="text-xl font-bold text-metis-gold">Arete</div>
                  </div>
                  <NavigationContent navigation={navigation} pathname={pathname} userRole={userRole} />
                </div>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </Dialog>
      </Transition.Root>

      {/* Desktop sidebar */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:z-50 lg:flex lg:w-64 lg:flex-col">
        <div className="flex grow flex-col gap-y-5 overflow-y-auto bg-card px-6 border-r border-border">
          <div className="flex h-16 shrink-0 items-center">
            <div className="text-xl font-bold text-metis-gold">Arete</div>
          </div>
          <NavigationContent navigation={navigation} pathname={pathname} userRole={userRole} />
        </div>
      </div>

      {/* Mobile menu button */}
      <div className="sticky top-0 z-40 flex items-center gap-x-6 bg-card px-4 py-4 shadow-sm sm:px-6 lg:hidden border-b border-border">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setIsMobileMenuOpen(true)}
        >
          <Menu className="h-6 w-6" />
        </Button>
        <div className="flex-1 text-sm font-semibold leading-6 text-foreground">
          Dashboard
        </div>
        <div className="text-xs text-muted-foreground capitalize">
          {userRole}
        </div>
      </div>
    </>
  );
}

interface NavigationContentProps {
  navigation: any[];
  pathname: string;
  userRole: 'coach' | 'client' | null;
}

function NavigationContent({ navigation, pathname, userRole }: NavigationContentProps) {
  return (
    <nav className="flex flex-1 flex-col">
      <ul role="list" className="flex flex-1 flex-col gap-y-7">
        {navigation.map((section) => (
          <li key={section.id}>
            <div className="text-xs font-semibold leading-6 text-muted-foreground uppercase tracking-wide">
              {section.title}
            </div>
            <ul role="list" className="mt-2 space-y-1">
              {section.items.map((item) => (
                <li key={item.id}>
                  <Link
                    href={item.href}
                    className={cn(
                      pathname === item.href
                        ? 'bg-accent text-accent-foreground'
                        : 'text-muted-foreground hover:text-foreground hover:bg-accent/50',
                      'group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-medium transition-colors'
                    )}
                  >
                    <item.icon className="h-5 w-5 shrink-0" />
                    <span className="truncate">{item.title}</span>
                    {item.badge && (
                      <span className="ml-auto inline-flex items-center rounded-full bg-primary px-2 py-1 text-xs font-medium text-primary-foreground">
                        {item.badge}
                      </span>
                    )}
                  </Link>
                </li>
              ))}
            </ul>
          </li>
        ))}
        
        {/* Role indicator */}
        <li className="mt-auto">
          <Card className="p-3">
            <div className="flex items-center gap-2">
              <div className={cn(
                "w-2 h-2 rounded-full",
                userRole === 'coach' ? 'bg-owlet-teal' : 'bg-metis-gold'
              )} />
              <span className="text-sm font-medium capitalize">{userRole}</span>
            </div>
          </Card>
        </li>
      </ul>
    </nav>
  );
}

function NavigationSkeleton() {
  return (
    <div className="hidden lg:fixed lg:inset-y-0 lg:z-50 lg:flex lg:w-64 lg:flex-col">
      <div className="flex grow flex-col gap-y-5 overflow-y-auto bg-card px-6 border-r border-border">
        <div className="flex h-16 shrink-0 items-center">
          <div className="h-6 w-16 bg-muted animate-pulse rounded" />
        </div>
        <div className="space-y-4">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="flex items-center gap-3">
              <div className="h-5 w-5 bg-muted animate-pulse rounded" />
              <div className="h-4 w-24 bg-muted animate-pulse rounded" />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
```

## 5. Navigation Utilities and Hooks

### Navigation Utilities

Create new file: [`frontend/src/components/navigation/NavigationUtils.tsx`](frontend/src/components/navigation/NavigationUtils.tsx)

```typescript
"use client";

import { usePathname } from 'next/navigation';
import { useNavigation } from './NavigationProvider';
import { getNavigationItem } from '@/config/navigation';

export function useCurrentNavigation() {
  const pathname = usePathname();
  const { navigation } = useNavigation();

  // Find current navigation item
  const currentItem = navigation
    .flatMap(section => section.items)
    .find(item => item.href === pathname);

  // Find breadcrumb trail
  const breadcrumbs = [];
  if (currentItem) {
    // Add section title
    const section = navigation.find(s => s.items.includes(currentItem));
    if (section && section.title !== 'Main') {
      breadcrumbs.push({ title: section.title, href: '#' });
    }
    breadcrumbs.push({ title: currentItem.title, href: currentItem.href });
  }

  return {
    currentItem,
    breadcrumbs,
    pageTitle: currentItem?.title || 'Dashboard'
  };
}

export function NavigationBreadcrumb() {
  const { breadcrumbs } = useCurrentNavigation();

  if (breadcrumbs.length <= 1) return null;

  return (
    <nav className="flex mb-4" aria-label="Breadcrumb">
      <ol className="flex items-center space-x-2 text-sm text-muted-foreground">
        {breadcrumbs.map((crumb, index) => (
          <li key={crumb.href} className="flex items-center">
            {index > 0 && <span className="mx-2">/</span>}
            <span className={index === breadcrumbs.length - 1 ? 'text-foreground font-medium' : ''}>
              {crumb.title}
            </span>
          </li>
        ))}
      </ol>
    </nav>
  );
}

export function PageHeader() {
  const { currentItem, pageTitle } = useCurrentNavigation();

  return (
    <div className="mb-6">
      <NavigationBreadcrumb />
      <div className="flex items-center gap-3">
        {currentItem?.icon && <currentItem.icon className="h-6 w-6 text-muted-foreground" />}
        <h1 className="text-2xl font-bold text-foreground">{pageTitle}</h1>
      </div>
      {currentItem?.description && (
        <p className="mt-2 text-muted-foreground">{currentItem.description}</p>
      )}
    </div>
  );
}
```

## 6. Responsive Design Implementation

### Mobile Navigation Enhancements

The navigation system includes several responsive features:

1. **Breakpoint Strategy**:
   - Mobile (< 1024px): Hamburger menu with slide-out drawer
   - Desktop (≥ 1024px): Fixed sidebar navigation
   - Uses Tailwind's `lg:` prefix for consistency

2. **Touch-Friendly Design**:
   - Minimum 44px touch targets on mobile
   - Adequate spacing between navigation items
   - Smooth transitions and animations

3. **Content Adaptation**:
   - Main content area adjusts with `lg:pl-64` for desktop sidebar
   - Mobile content uses full width with top navigation bar
   - Proper z-index layering for overlays

## 7. Styling and UI Integration

### Design System Integration

The navigation leverages existing Arete design tokens:

```typescript
// Color Usage
- Primary navigation: Uses `bg-card` and `text-foreground`
- Active states: Uses `bg-accent` and `text-accent-foreground`
- Brand accent: Uses `text-metis-gold` for logo
- Role indicators: Uses `bg-owlet-teal` (coach) and `bg-metis-gold` (client)

// Typography
- Navigation items: Uses `text-sm font-medium`
- Section headers: Uses `text-xs font-semibold uppercase tracking-wide`
- Page titles: Uses `text-2xl font-bold`

// Spacing and Layout
- Sidebar width: `w-64` (256px) on desktop
- Content padding: `px-4 sm:px-6 lg:px-8`
- Navigation item spacing: `space-y-1` and `gap-x-3`
```

### Component Dependencies

The navigation system uses these existing UI components:
- [`Button`](frontend/src/components/ui/button.tsx) - For menu toggles and actions
- [`Card`](frontend/src/components/ui/card.tsx) - For role indicator and mobile panels
- Headless UI - For mobile menu transitions and accessibility
- Lucide React - For consistent iconography

## 8. Implementation Steps

### Phase 1: Core Infrastructure (Days 1-2)
1. **Create Navigation Configuration**
   - [ ] Create [`frontend/src/config/navigation.ts`](frontend/src/config/navigation.ts)
   - [ ] Define navigation structure with role-based filtering
   - [ ] Add icon imports and type definitions

2. **Install Dependencies**
   ```bash
   cd frontend
   npm install @headlessui/react lucide-react
   ```

### Phase 2: Context and Provider (Days 3-4)
3. **Create Navigation Provider**
   - [ ] Create [`frontend/src/components/navigation/NavigationProvider.tsx`](frontend/src/components/navigation/NavigationProvider.tsx)
   - [ ] Implement role detection and navigation filtering
   - [ ] Add mobile menu state management

4. **Create Navigation Utilities**
   - [ ] Create [`frontend/src/components/navigation/NavigationUtils.tsx`](frontend/src/components/navigation/NavigationUtils.tsx)
   - [ ] Implement breadcrumb and page header components
   - [ ] Add current navigation detection hooks

### Phase 3: Main Navigation Component (Days 5-6)
5. **Create DashboardNav Component**
   - [ ] Create [`frontend/src/components/navigation/DashboardNav.tsx`](frontend/src/components/navigation/DashboardNav.tsx)
   - [ ] Implement responsive sidebar/mobile menu
   - [ ] Add proper accessibility attributes and keyboard navigation

6. **Create Dashboard Layout**
   - [ ] Create [`frontend/src/app/dashboard/layout.tsx`](frontend/src/app/dashboard/layout.tsx)
   - [ ] Integrate navigation provider and main navigation
   - [ ] Ensure proper content area spacing

### Phase 4: Integration and Testing (Days 7-8)
7. **Update Existing Pages**
   - [ ] Remove individual page navigation implementations
   - [ ] Add PageHeader components to dashboard pages
   - [ ] Test navigation on all existing dashboard routes

8. **Responsive Testing**
   - [ ] Test mobile menu functionality across devices
   - [ ] Verify touch targets and accessibility
   - [ ] Ensure proper content flow and spacing

### Phase 5: Polish and Documentation (Days 9-10)
9. **Add Loading States and Error Handling**
   - [ ] Implement navigation skeleton loading state
   - [ ] Add error boundaries for navigation failures
   - [ ] Handle edge cases (missing user role, etc.)

10. **Documentation and Cleanup**
    - [ ] Document navigation configuration patterns
    - [ ] Add JSDoc comments to all components
    - [ ] Clean up any unused navigation code from individual pages

## 9. Role-Based Navigation Details

### Coach Navigation Items
```typescript
// Coach-specific sections and items
- Client Overview: Analytics and progress tracking
- Session Planning: Calendar and session management
- Coaching Notes: Session documentation
- All standard items: Dashboard, Connections, Documents, Goals, Insights
```

### Client Navigation Items
```typescript
// Client-focused navigation
- Personal Dashboard: Goal progress and insights
- My Coach: Connection management
- Documents: Personal document library
- Goals: Personal goal tracking
- Session Insights: Session analysis and feedback
```

### Dynamic Navigation Features
- Badge support for notifications and counts
- Role indicator in sidebar footer
- Conditional menu items based on user permissions
- Future support for nested navigation items

## 10. Accessibility and Performance

### Accessibility Features
- **Keyboard Navigation**: Full keyboard support with proper focus management
- **Screen Reader Support**: Proper ARIA labels and landmarks
- **High Contrast**: Uses semantic color tokens for theme compatibility
- **Focus Indicators**: Clear focus states for all interactive elements

### Performance Optimizations
- **Code Splitting**: Navigation components are client-side only where needed
- **Lazy Loading**: Icons and heavy components load on demand
- **Memoization**: Navigation configuration is memoized to prevent re-renders
- **Efficient Re-renders**: Context updates only trigger necessary component updates

## 11. Future Enhancements

### Phase 2 Features (Post-MVP)
- **Nested Navigation**: Support for sub-menus and hierarchical navigation
- **Customizable Layout**: User preferences for sidebar width and position
- **Navigation Search**: Quick navigation with command palette
- **Recent Pages**: Track and display recently visited pages

### Advanced Features
- **Contextual Navigation**: Dynamic menu items based on current page context
- **Notification Integration**: Real-time badges and alerts in navigation
- **Keyboard Shortcuts**: Global shortcuts for common navigation actions
- **Analytics Integration**: Track navigation usage patterns

## 12. Testing Strategy

### Unit Tests
- Navigation configuration filtering logic
- Role-based menu item visibility
- Mobile menu state management
- Breadcrumb generation logic

### Integration Tests
- Navigation provider context functionality
- Route-based active state detection
- Responsive behavior across breakpoints
- Accessibility compliance testing

### User Acceptance Testing
- Coach workflow navigation testing
- Client experience validation
- Mobile device testing across platforms
- Cross-browser compatibility verification

## Success Criteria

### MVP Requirements
- ✅ Unified layout component wraps all dashboard pages
- ✅ Mobile-first responsive navigation with sidebar/hamburger adaptation
- ✅ Role-based navigation with different items for coaches vs clients
- ✅ Consistent UI using existing Arete design system components
- ✅ Proper accessibility support and keyboard navigation
- ✅ Clean integration with existing dashboard pages

### Quality Requirements
- ✅ Smooth animations and transitions on all devices
- ✅ Fast navigation switching with minimal re-renders
- ✅ Proper loading states and error handling
- ✅ Scalable configuration system for future navigation items
- ✅ Comprehensive documentation for future development

### Technical Requirements
- ✅ TypeScript implementation with proper type safety
- ✅ Follows established Arete architectural patterns
- ✅ Minimal bundle size impact with efficient code splitting
- ✅ Cross-browser compatibility (Chrome, Firefox, Safari, Edge)
- ✅ Mobile performance optimization for touch interactions

This comprehensive navigation system will provide a solid foundation for the Arete dashboard experience, ensuring consistency, scalability, and excellent user experience across all devices and user roles.