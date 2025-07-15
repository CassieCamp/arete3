"use client";

import { ReactNode } from 'react';
import { usePathname } from 'next/navigation';
import { TopNav } from '@/components/navigation/TopNav';
import { BottomNavigation } from '@/components/navigation/BottomNavigation';
import { NavigationProvider } from '@/components/navigation/NavigationProvider';

interface AppLayoutProps {
  children: ReactNode;
  suppressBottomNav?: boolean;
}

// Utility function to determine active tab based on pathname
function getActiveTab(pathname: string): 'mountain' | 'microphone' | 'compass' | 'center' | null {
  if (pathname.includes('/member/journey') || pathname.includes('/journey') || pathname.includes('/mountain')) {
    return 'mountain';
  } else if (pathname.includes('/member/center') || pathname.includes('/center')) {
    return 'center';
  } else if (pathname.includes('/member/coaching') || pathname.includes('/coaching')) {
    return 'compass';
  } else if (pathname.includes('/coach')) {
    return 'compass';
  } else {
    // No active tab for base dashboard route
    return null;
  }
}

export function AppLayout({ children, suppressBottomNav = false }: AppLayoutProps) {
  const pathname = usePathname();
  const activeTab = getActiveTab(pathname);

  return (
    <NavigationProvider>
      <div className="min-h-screen bg-background">
        {/* Top Navigation */}
        <TopNav activeTab={activeTab} />
        
        {/* Main Content */}
        <main className={`py-6 ${suppressBottomNav ? 'pb-6' : 'pb-20 md:pb-6'}`}>
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            {children}
          </div>
        </main>
        
        {/* Bottom Navigation - Mobile only, conditionally rendered */}
        {!suppressBottomNav && (
          <div className="md:hidden">
            <BottomNavigation activeTab={activeTab} />
          </div>
        )}
      </div>
    </NavigationProvider>
  );
}