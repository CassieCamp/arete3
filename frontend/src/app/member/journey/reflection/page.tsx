'use client';

import React from 'react';
import { AppLayout } from '@/components/layout/AppLayout';
import { ThreeIconNav } from '@/components/navigation/ThreeIconNav';
import { CenterReflectionCreator } from '../../../../components/journey/CenterReflectionCreator';

export default function ReflectionPage() {
  return (
    <AppLayout suppressBottomNav={true}>
      <ThreeIconNav />
      <div className="container mx-auto px-4 py-8 md:pt-20 pb-20">
        <CenterReflectionCreator />
      </div>
    </AppLayout>
  );
}