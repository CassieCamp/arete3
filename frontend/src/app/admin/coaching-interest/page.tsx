'use client';

import { PageHeader } from '@/components/ui/page-header';
import { AppLayout } from '@/components/layout/AppLayout';
import { CoachingInterestList } from '@/components/admin/CoachingInterestList';
import { RoleGuard } from '@/components/auth/RoleGuard';
import { Users } from 'lucide-react';

export default function CoachingInterestPage() {
  return (
    <AppLayout>
      <RoleGuard requiredRoles={['admin']}>
        <div className="container mx-auto px-4 py-8 md:pt-20 pb-20">
          <PageHeader
            icon={Users}
            title="Coaching Interest Submissions"
            subtitle="View and manage coaching interest submissions from potential clients"
          />
          
          <div className="w-full max-w-6xl mx-auto">
            <CoachingInterestList />
          </div>
        </div>
      </RoleGuard>
    </AppLayout>
  );
}