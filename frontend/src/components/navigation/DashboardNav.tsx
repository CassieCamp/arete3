"use client";

import { Fragment } from 'react';
import { usePathname } from 'next/navigation';
import Link from 'next/link';
import { Dialog, Transition } from '@headlessui/react';
import { X, Menu } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { useNavigation } from './NavigationProvider';
import { NavigationSection } from '@/config/navigation';
import { NotificationBell } from '@/components/notifications/NotificationBell';
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
            <div className="fixed inset-0 bg-background/80" />
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
                
                <div className="flex grow flex-col gap-y-5 overflow-y-auto bg-sidebar px-6 pb-2 ring-1 ring-sidebar-border/10">
                  <div className="flex h-16 shrink-0 items-center">
                    <Link href="/" className="text-xl font-serif font-bold text-primary hover:text-primary/80 transition-colors">
                      Arete
                    </Link>
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
        <div className="flex grow flex-col gap-y-5 overflow-y-auto bg-sidebar px-6 border-r border-sidebar-border">
          <div className="flex h-16 shrink-0 items-center justify-between">
            <Link href="/" className="text-xl font-serif font-bold text-primary hover:text-primary/80 transition-colors">
              Arete
            </Link>
            <NotificationBell />
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
        <NotificationBell />
        <div className="text-xs text-muted-foreground capitalize">
          {userRole}
        </div>
      </div>
    </>
  );
}

interface NavigationContentProps {
  navigation: NavigationSection[];
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
                userRole === 'coach' ? 'bg-primary' : 'bg-secondary'
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