"use client";

import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { useNavigation } from './NavigationProvider';
import { useEntryModal } from '@/context/EntryModalContext';
import { MainNavigationItem } from '@/config/navigation';

interface BottomNavigationProps {
  activeTab: 'mountain' | 'microphone' | 'compass' | 'center' | null;
  className?: string;
}

export function BottomNavigation({
  activeTab,
  className = ""
}: BottomNavigationProps) {
  const router = useRouter();
  const { mainNavigation, isLoading } = useNavigation();
  const { openEntryModal } = useEntryModal();
  
  const handleNavigation = (item: MainNavigationItem) => {
    if (item.action === 'openEntryModal') {
      openEntryModal();
    } else if (item.href) {
      router.push(item.href);
    }
  };
  
  // Don't render anything while navigation is loading
  if (isLoading) {
    return null;
  }
  
  return (
    <div className={`fixed bottom-0 left-0 right-0 bg-background border-t border-border px-4 py-2 z-50 ${className}`}>
      <div className="flex justify-around items-center max-w-md mx-auto">
        {mainNavigation.map((item, index) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          
          return (
            <div key={item.id} className="relative">
              
              {/* Navigation Button */}
              <Button
                variant="ghost"
                size="lg"
                onClick={() => handleNavigation(item)}
                className={`p-3 rounded-full transition-all duration-200 flex flex-col items-center justify-center gap-1 min-h-[60px] ${
                  isActive
                    ? 'text-primary bg-primary/10 scale-110'
                    : 'text-muted-foreground hover:text-foreground hover:bg-accent'
                }`}
              >
                <Icon className="w-6 h-6 flex-shrink-0" />
                <span className="text-xs font-medium leading-none">{item.label}</span>
              </Button>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// Simplified version without tooltips for general use
export function SimpleBottomNavigation({
  activeTab,
  className = ""
}: {
  activeTab: 'mountain' | 'microphone' | 'compass' | 'center' | null;
  className?: string;
}) {
  return (
    <BottomNavigation
      activeTab={activeTab}
      className={className}
    />
  );
}