'use client';

import React from 'react';
import { useRouter } from 'next/navigation';

const SimpleJourneyTest: React.FC = () => {
  const router = useRouter();

  const handleAddReflection = () => {
    router.push('/member/journey/reflection');
  };

  return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center p-8">
      <div className="text-center max-w-4xl">
        <div className="bg-slate-900/90 backdrop-blur-sm rounded-2xl p-8 md:p-12 shadow-2xl">
          <p className="text-4xl md:text-5xl font-serif italic text-white leading-relaxed tracking-wide">
            Your journey begins with reflection.{' '}
            <span className="text-white font-medium">
              Add your first reflection to get started.
            </span>
          </p>
        </div>
      </div>
      
      <button 
        onClick={handleAddReflection}
        className="fixed bottom-24 right-6 w-16 h-16 bg-slate-800 text-white border-2 border-white rounded-full flex items-center justify-center hover:scale-110 transition-transform shadow-lg"
      >
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M12 5V19M5 12H19" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      </button>
    </div>
  );
};

export default SimpleJourneyTest;