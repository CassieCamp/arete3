'use client';

import React from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useUser } from '@clerk/nextjs';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { useNavigation } from './NavigationProvider';
import { useEntryModal } from '@/context/EntryModalContext';
import { MainNavigationItem } from '@/config/navigation';

interface TopNavProps {
  activeTab: 'mountain' | 'microphone' | 'compass' | 'basecamp' | null;
  className?: string;
}

export function TopNav({
  activeTab,
  className = ""
}: TopNavProps) {
  const {
    mainNavigation
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
    const userRole = user?.publicMetadata?.role || 'client';
    
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

  return (
    <nav className={cn(
      "bg-background/95 backdrop-blur-sm border-b border-gray-200 sticky top-0 z-50",
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
            })}
          </div>

          {/* Right side - Empty space for balance */}
          <div className="flex items-center">
            {/* This space can be used for user avatar or other actions later */}
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
  activeTab: 'mountain' | 'microphone' | 'compass' | 'basecamp' | null;
  className?: string;
}) {
  return (
    <TopNav
      activeTab={activeTab}
      className={className}
    />
  );
}