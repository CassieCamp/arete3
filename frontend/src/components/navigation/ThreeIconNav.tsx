"use client";

import { useRouter, usePathname } from 'next/navigation';
import { useUser, UserButton } from '@clerk/nextjs';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { Route, Tent, Users } from 'lucide-react';
import { AuthDropdown } from '@/components/auth/AuthDropdown';

interface ThreeIconNavProps {
  className?: string;
}

// Navigation items specifically for the three-icon nav
const NAV_ITEMS = [
  {
    id: 'journey',
    icon: Route,
    label: 'Journey',
    href: '/journey'
  },
  {
    id: 'basecamp',
    icon: Tent,
    label: 'Basecamp',
    href: '/basecamp'
  },
  {
    id: 'coach',
    icon: Users,
    label: 'Coach',
    href: '/coach'
  }
] as const;

export function ThreeIconNav({ className = "" }: ThreeIconNavProps) {
  const router = useRouter();
  const pathname = usePathname();
  const { user } = useUser();

  const handleNavigation = (href: string) => {
    router.push(href);
  };

  const isActive = (href: string) => {
    return pathname === href || pathname.startsWith(href + '/');
  };

  return (
    <>
      {/* Desktop Header - Hidden on mobile */}
      <div className={cn(
        "hidden md:flex fixed top-0 left-0 right-0 bg-background/95 backdrop-blur-sm border-b border-border px-4 py-3 z-50",
        className
      )}>
        <div className="flex justify-between items-center w-full max-w-6xl mx-auto">
          {/* Left side - Logo */}
          <div className="flex items-center">
            <h1 className="text-2xl font-serif font-bold text-gray-900 dark:text-white">
              Arete
            </h1>
          </div>
          
          {/* Center - Navigation Items */}
          <div className="flex justify-center items-center gap-8">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const active = isActive(item.href);
            
            return (
              <Button
                key={item.id}
                variant="ghost"
                size="sm"
                onClick={() => handleNavigation(item.href)}
                className={cn(
                  "flex flex-col items-center gap-1 p-3 h-auto transition-all duration-200",
                  active
                    ? 'text-primary bg-primary/10'
                    : 'text-muted-foreground hover:text-foreground hover:bg-accent'
                )}
              >
                <Icon className="w-5 h-5" />
                <span className="text-xs font-medium">{item.label}</span>
              </Button>
            );
          })}
          </div>
          
          {/* Right side - User Avatar */}
          <div className="flex items-center">
            {user ? (
              <UserButton
                appearance={{
                  elements: {
                    avatarBox: "w-8 h-8"
                  }
                }}
              />
            ) : (
              <AuthDropdown variant="ghost" />
            )}
          </div>
        </div>
      </div>

      {/* Mobile Footer - Hidden on desktop */}
      <div className={cn(
        "md:hidden fixed bottom-0 left-0 right-0 bg-background/95 backdrop-blur-sm border-t border-border px-4 py-2 z-50",
        className
      )}>
        <div className="flex justify-around items-center max-w-md mx-auto">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const active = isActive(item.href);
            
            return (
              <Button
                key={item.id}
                variant="ghost"
                size="lg"
                onClick={() => handleNavigation(item.href)}
                className={cn(
                  "p-3 rounded-full transition-all duration-200 flex flex-col items-center gap-1",
                  active
                    ? 'text-primary bg-primary/10 scale-110'
                    : 'text-muted-foreground hover:text-foreground hover:bg-accent'
                )}
              >
                <Icon className="w-6 h-6" />
                <span className="text-xs font-medium">{item.label}</span>
              </Button>
            );
          })}
        </div>
      </div>
    </>
  );
}