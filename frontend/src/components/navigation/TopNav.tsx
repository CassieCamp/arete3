'use client';

import React from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useUser, UserButton } from '@clerk/nextjs';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { useNavigation } from './NavigationProvider';
import { useEntryModal } from '@/context/EntryModalContext';
import { MainNavigationItem } from '@/config/navigation';
import { AuthDropdown } from '@/components/auth/AuthDropdown';

// Clerk UserButton appearance configuration
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
    avatarBox: "w-8 h-8",
    userButtonPopoverCard: "w-64 p-1 bg-popover border border-border rounded-md shadow-md",
    userButtonPopoverActionButton: "w-full justify-start p-2 text-sm font-medium rounded-sm hover:bg-accent transition-colors",
    userPreview: "flex items-center gap-3 p-2 rounded-sm hover:bg-accent transition-colors",
    userButtonPopoverFooter: "border-t border-border pt-2 mt-2"
  }
};

interface TopNavProps {
  activeTab: 'mountain' | 'microphone' | 'compass' | 'center' | null;
  className?: string;
}

export function TopNav({
  activeTab,
  className = ""
}: TopNavProps) {
  const {
    mainNavigation,
    isLoading
  } = useNavigation();
  const router = useRouter();
  const { user } = useUser();
  const { openEntryModal } = useEntryModal();
  
  const handleNavigation = (item: MainNavigationItem) => {
    if (item.action === 'openEntryModal') {
      openEntryModal();
    } else if (item.href) {
      router.push(item.href);
    }
  };


  // Role-based routing for compass/coach icon
  const getCompassHref = () => {
    const userRole = user?.publicMetadata?.primary_role || 'member';
    
    if (userRole === 'coach') {
      return '/coach'; // Coach dashboard
    } else {
      return '/coach'; // Client coach connection page
    }
  };

  // Update compass navigation item with role-based href
  const updatedNavigationItems = mainNavigation.map(item => {
    if (item.id === 'compass') {
      return {
        ...item,
        href: getCompassHref()
      };
    }
    return item;
  });

  // Don't render navigation items while loading
  if (isLoading) {
    return (
      <nav className={cn(
        "bg-background/95 backdrop-blur-sm border-b border-gray-200 border-t-0 sticky top-0 z-50 -mt-px pt-px",
        className
      )}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Left side - Logo/Brand area */}
            <div className="flex items-center">
              <Link href="/">
                <h1 className="text-2xl font-serif font-bold text-gray-900 dark:text-white cursor-pointer hover:opacity-80 transition-opacity">
                  Arete
                </h1>
              </Link>
            </div>

            {/* Right side - Authentication */}
            <div className="flex items-center gap-4">
              {user ? (
                <UserButton
                  appearance={clerkAppearance}
                  afterSignOutUrl="/"
                  userProfileMode="modal"
                  showName={false}
                />
              ) : (
                <AuthDropdown variant="ghost" />
              )}
            </div>
          </div>
        </div>
      </nav>
    );
  }

  return (
    <nav className={cn(
      "bg-background/95 backdrop-blur-sm border-b border-gray-200 border-t-0 sticky top-0 z-50 -mt-px pt-px",
      className
    )}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Left side - Logo/Brand area */}
          <div className="flex items-center">
            <Link href="/">
              <h1 className="text-2xl font-serif font-bold text-gray-900 dark:text-white cursor-pointer hover:opacity-80 transition-opacity">
                Arete
              </h1>
            </Link>
          </div>

          {/* Center - Main Navigation Items (Desktop only) */}
          <div className="hidden md:flex items-center space-x-8">
            {updatedNavigationItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              
              // Handle special actions like opening entry modal
              if (item.action === 'openEntryModal') {
                return (
                  <Button
                    key={item.id}
                    variant="ghost"
                    onClick={() => handleNavigation(item)}
                    className={cn(
                      "flex items-center gap-2 px-4 py-2 rounded-lg transition-all duration-200",
                      isActive
                        ? 'text-primary bg-primary/10 font-medium'
                        : 'text-foreground hover:text-foreground hover:bg-gray-100'
                    )}
                  >
                    <Icon className="w-5 h-5" />
                    <span className="font-medium">{item.label}</span>
                  </Button>
                );
              }
              
              // Use Link for navigation items with href
              return (
                <Link key={item.id} href={item.href || '#'}>
                  <Button
                    variant="ghost"
                    className={cn(
                      "flex items-center gap-2 px-4 py-2 rounded-lg transition-all duration-200",
                      isActive
                        ? 'text-primary bg-primary/10 font-medium'
                        : 'text-foreground hover:text-foreground hover:bg-gray-100'
                    )}
                  >
                    <Icon className="w-5 h-5" />
                    <span className="font-medium">{item.label}</span>
                  </Button>
                </Link>
              );
            })}
          </div>

          {/* Right side - Authentication */}
          <div className="flex items-center gap-4">
            {user ? (
              <UserButton
                appearance={clerkAppearance}
                afterSignOutUrl="/"
                userProfileMode="modal"
                showName={false}
              />
            ) : (
              <AuthDropdown variant="ghost" />
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}

// Simplified version for general use
export function SimpleTopNav({
  activeTab,
  className = ""
}: {
  activeTab: 'mountain' | 'microphone' | 'compass' | 'center' | null;
  className?: string;
}) {
  return (
    <TopNav
      activeTab={activeTab}
      className={className}
    />
  );
}