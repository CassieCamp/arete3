"use client";

import { ReactNode } from 'react';
import DashboardNav from '@/components/navigation/DashboardNav';
import { NavigationProvider } from '@/components/navigation/NavigationProvider';
import { OnboardingGuide } from '@/components/onboarding/OnboardingGuide';

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
        
        {/* Onboarding Guide - Shows as overlay when needed */}
        <OnboardingGuide />
      </div>
    </NavigationProvider>
  );
}