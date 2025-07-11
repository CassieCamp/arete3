'use client';

import { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { CenterTab } from '@/components/mountain/CenterTab';
import { JourneyTab } from '@/components/mountain/JourneyTab';
import { DestinationsTab } from '@/components/mountain/DestinationsTab';

export default function MountainPage() {
  const [activeTab, setActiveTab] = useState('center');

  return (
    <div className="min-h-screen bg-background pb-20">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">Mountain Navigation</h1>
          <p className="text-gray-600 dark:text-gray-300">Your journey of growth and discovery</p>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full max-w-4xl mx-auto">
          <TabsList className="grid w-full grid-cols-2 mb-8">
            <TabsTrigger value="center" className="flex items-center gap-2">
              🏕️ Center
            </TabsTrigger>
            <TabsTrigger value="journey" className="flex items-center gap-2">
              🗺️ Journey
            </TabsTrigger>
          </TabsList>

          <TabsContent value="center">
            <CenterTab />
          </TabsContent>

          <TabsContent value="journey">
            <JourneyTab />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}