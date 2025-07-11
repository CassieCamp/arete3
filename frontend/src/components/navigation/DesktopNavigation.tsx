'use client';

import React from 'react';
import { usePathname, useRouter } from 'next/navigation';
import { useUser } from '@clerk/nextjs';
import {
  Menu,
  X
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { useNavigation } from './NavigationProvider';
import { useEntryModal } from '@/context/EntryModalContext';
import { MainNavigationItem, MenuNavigationItem } from '@/config/navigation';

interface DesktopNavigationProps {
  activeTab: 'mountain' | 'microphone' | 'compass' | 'basecamp' | null;
  className?: string;
}

export function DesktopNavigation({
  activeTab,
  className = ""
}: DesktopNavigationProps) {
  const {
    mainNavigation,
    menuNavigation,
    isMobileMenuOpen,
    setIsMobileMenuOpen,
    userRole
  } = useNavigation();
  const router = useRouter();
  const pathname = usePathname();
  const { user } = useUser();
  const { openEntryModal } = useEntryModal();
  
  const handleNavigation = (item: MainNavigationItem) => {
    if (item.action === 'openEntryModal') {
      openEntryModal();
    } else if (item.href) {
      router.push(item.href);
    }
  };

  const handleMenuNavigation = (href: string) => {
    router.push(href);
    setIsMobileMenuOpen(false);
  };

  const toggleMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  // Role-based routing for compass/coach icon
  const getCompassHref = () => {
    // Placeholder logic for role-based behavior
    // TODO: Implement actual role detection logic
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
    <div className={cn(
      "fixed left-0 top-0 h-full w-20 bg-background border-r border-border z-50 flex flex-col",
      className
    )}>
      {/* Hamburger Menu Button */}
      <div className="p-4 border-b border-border">
        <Button
          variant="ghost"
          size="sm"
          onClick={toggleMenu}
          className="w-full h-12 p-0 hover:bg-accent"
        >
          {isMobileMenuOpen ? (
            <X className="w-6 h-6" />
          ) : (
            <Menu className="w-6 h-6" />
          )}
        </Button>
      </div>

      {/* Main Navigation Items */}
      <div className="flex-1 flex flex-col justify-center gap-4 p-4">
        {updatedNavigationItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          
          return (
            <div key={item.id} className="relative group">
              <Button
                variant="ghost"
                size="lg"
                onClick={() => handleNavigation(item)}
                className={cn(
                  "w-full h-12 p-0 rounded-xl transition-all duration-200 flex flex-col items-center justify-center gap-1",
                  isActive
                    ? 'text-primary bg-primary/10 scale-105'
                    : 'text-muted-foreground hover:text-foreground hover:bg-accent'
                )}
              >
                <Icon className="w-6 h-6" />
                <span className="text-xs font-medium">{item.label}</span>
              </Button>

            </div>
          );
        })}
      </div>

      {/* Hamburger Menu Overlay */}
      {isMobileMenuOpen && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 bg-black/20 z-40"
            onClick={() => setIsMobileMenuOpen(false)}
          />
          
          {/* Menu Panel */}
          <div className="fixed left-20 top-0 h-full w-64 bg-background border-r border-border z-50 shadow-lg">
            <div className="p-4 border-b border-border">
              <h3 className="font-semibold text-lg">Menu</h3>
            </div>
            
            <div className="p-4 space-y-2">
              {menuNavigation.map((link) => {
                const Icon = link.icon;
                const isCurrentPage = pathname === link.href;
                
                return (
                  <Button
                    key={link.id}
                    variant="ghost"
                    onClick={() => handleMenuNavigation(link.href)}
                    className={cn(
                      "w-full justify-start gap-3 h-12",
                      isCurrentPage && "bg-accent text-accent-foreground"
                    )}
                  >
                    <Icon className="w-5 h-5" />
                    <span>{link.label}</span>
                  </Button>
                );
              })}
            </div>
          </div>
        </>
      )}
    </div>
  );
}

// Simplified version for general use
export function SimpleDesktopNavigation({
  activeTab,
  className = ""
}: {
  activeTab: 'mountain' | 'microphone' | 'compass' | 'basecamp' | null;
  className?: string;
}) {
  return (
    <DesktopNavigation
      activeTab={activeTab}
      className={className}
    />
  );
}