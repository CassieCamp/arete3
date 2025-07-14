"use client";

import { useParams, useRouter } from 'next/navigation';
import { useUser } from '@clerk/nextjs';
import { useSessionInsight } from "@/hooks/useSessionInsight";
import { useInsightNavigation } from "@/hooks/useInsightNavigation";
import { SessionInsightModal } from "@/components/insights/SessionInsightModal";
import { useEffect, useState } from 'react';

export default function DynamicInsightPage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;
  const { insight, loading, error, refetch } = useSessionInsight(id);
  const navigation = useInsightNavigation(id);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Open modal when component mounts and we have data
  useEffect(() => {
    if (!loading && (insight || error)) {
      setIsModalOpen(true);
    }
  }, [loading, insight, error]);

  const handleClose = () => {
    setIsModalOpen(false);
    // Small delay to allow modal close animation before navigation
    setTimeout(() => {
      router.push('/member/journey');
    }, 150);
  };

  return (
    <>
      {/* Background overlay when modal is open - provides context that we're still on the journey page */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-40" />
      )}
      
      <SessionInsightModal
        insight={insight}
        isOpen={isModalOpen}
        onClose={handleClose}
        loading={loading}
        error={error}
        navigation={navigation}
      />
    </>
  );
}