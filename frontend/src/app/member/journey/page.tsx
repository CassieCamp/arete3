'use client';

import { useState } from 'react';
import { useJourneyData } from '@/hooks/useJourneyData';
import { ReflectionUploadModal } from '@/components/ReflectionUploadModal';
import EmptyState from '@/components/journey/EmptyState';
import { Plus } from 'lucide-react';
import { AppLayout } from '@/components/layout/AppLayout';
import { ThreeIconNav } from '@/components/navigation/ThreeIconNav';
import { PageHeader } from '@/components/ui/page-header';
import { Route } from 'lucide-react';
import { MeanderingPathway } from '@/components/journey';
import { InsightCard } from '@/components/InsightCard';

export default function JourneyPage() {
  const { reflections, loading, uploading, uploadDocument } = useJourneyData();
  const [uploadModalOpen, setUploadModalOpen] = useState(false);

  const handlePlusClick = () => {
    setUploadModalOpen(true); // Always open upload modal
  };

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
                    {/* Show empty state when no reflections exist */}
                    {reflections.length === 0 && !loading && (
                      <EmptyState />
                    )}
                    
                    {/* Show reflections feed when reflections exist */}
                    {reflections.length > 0 && (
                      <div className="space-y-4">
                        {reflections.map((reflection, index) => (
                          <InsightCard key={reflection.id || index} reflection={reflection} />
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </AppLayout>
        </div>
      </div>
      
      {/* Plus button - always visible, always uploads */}
      <div className="fixed bottom-24 right-6 z-50">
        <button 
          onClick={handlePlusClick}
          className="w-16 h-16 rounded-full bg-slate-900/90 backdrop-blur-sm border-2 border-white flex items-center justify-center group shadow-2xl hover:scale-110 transition-transform"
          style={{
            boxShadow: `
              0 0 0 0 rgba(255, 255, 255, 0.6),
              0 0 20px rgba(255, 255, 255, 0.5),
              0 0 40px rgba(255, 255, 255, 0.4),
              0 0 60px rgba(255, 255, 255, 0.3),
              0 4px 12px rgba(0, 0, 0, 0.3)
            `
          }}
        >
          <Plus className="w-8 h-8 text-white" />
        </button>
      </div>

      <ReflectionUploadModal
        isOpen={uploadModalOpen}
        onClose={() => setUploadModalOpen(false)}
        onUpload={uploadDocument}
        uploading={uploading}
      />

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