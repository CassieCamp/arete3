'use client';

import { JourneyTab } from '@/components/mountain/JourneyTab';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { ThreeIconNav } from '@/components/navigation/ThreeIconNav';
import { PageHeader } from '@/components/ui/page-header';
import { Route } from 'lucide-react';

export default function JourneyPage() {
  return (
    <DashboardLayout>
      <ThreeIconNav />
      <div className="container mx-auto px-4 py-8 md:pt-20 pb-20">
        <PageHeader
          icon={Route}
          title="Journey"
          subtitle="Track your progress and growth over time"
        />

        <div className="w-full max-w-4xl mx-auto">
          <JourneyTab />
        </div>
      </div>
    </DashboardLayout>
  );
}