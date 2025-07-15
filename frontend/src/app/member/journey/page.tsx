'use client';

// import { JourneyTab } from '@/components/mountain/JourneyTab';  // REMOVED: component deprecated
import { AppLayout } from '@/components/layout/AppLayout';
import { ThreeIconNav } from '@/components/navigation/ThreeIconNav';
import { PageHeader } from '@/components/ui/page-header';
import { MeanderingPathway } from '@/components/journey';
import EmptyState from '@/components/journey/EmptyState';
import { Route } from 'lucide-react';

export default function JourneyPage() {
  return (
    <div className="relative min-h-screen">
      {/* Background meandering pathway - full viewport */}
      <MeanderingPathway />
      
      {/* Gradient fade overlay for top section */}
      <div className="absolute inset-x-0 top-0 h-40 bg-gradient-to-b from-slate-800 via-slate-800/80 to-transparent z-10 pointer-events-none" />
      
      {/* Custom layout for Journey page to override AppLayout constraints */}
      <div className="relative z-20 min-h-screen">
        {/* Navigation components with transparent background */}
        <div className="relative z-30">
          <AppLayout suppressBottomNav={true}>
            <div className="absolute inset-0 -z-10" /> {/* Remove AppLayout background */}
            <ThreeIconNav />
            <div className="min-h-screen flex flex-col relative -mt-6 -mb-20 md:-mb-6">
              {/* Main content with higher z-index - white text for dark background */}
              <div className="flex-1 flex flex-col items-center justify-start pt-8 md:pt-20 px-4 relative z-10 text-foreground">
                <div className="w-full max-w-3xl">
                  <PageHeader
                    icon={Route}
                    title="Journey"
                    className="[&_h1]:text-white [&_svg]:text-white"
                  />
                  <div className="mt-8">
                    {/* <JourneyTab /> */}
                    <EmptyState />
                  </div>
                </div>
              </div>
            </div>
          </AppLayout>
        </div>
      </div>
      
      {/* Override AppLayout background and TopNav border with custom styles */}
      <style jsx global>{`
        .min-h-screen.bg-background {
          background: transparent !important;
        }
        /* Remove TopNav border on Journey page */
        nav.bg-background\\/95 {
          border-bottom: none !important;
        }
      `}</style>
    </div>
  );
}