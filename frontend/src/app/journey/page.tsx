'use client';

import React, { useState } from 'react';
import { Plus } from 'lucide-react';

export default function JourneyPage() {
  const [uploadModalOpen, setUploadModalOpen] = useState(false);

  return (
    <div className="min-h-screen bg-gray-100 relative">
      {/* Header */}
      <div className="bg-white px-6 py-4 flex items-center justify-between border-b border-gray-200">
        <h1 className="text-2xl font-bold text-gray-900">Arete</h1>
        <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
            <circle cx="12" cy="7" r="4"/>
          </svg>
        </div>
      </div>

      {/* Main Content */}
      <div className="relative min-h-[calc(100vh-80px)] bg-gradient-to-br from-slate-800 via-slate-700 to-slate-900 overflow-hidden">
        
        {/* Flowing curves background */}
        <div className="absolute inset-0 pointer-events-none">
          <svg
            className="absolute w-full h-full opacity-30"
            viewBox="0 0 1000 1000"
            preserveAspectRatio="xMidYMid slice"
          >
            <path
              d="M-100,200 Q300,100 600,200 T1100,150 L1100,1000 L-100,1000 Z"
              fill="url(#curve1)"
            />
            <path
              d="M-100,600 Q400,500 700,600 T1200,550 L1200,1000 L-100,1000 Z"
              fill="url(#curve2)"
            />
            <defs>
              <linearGradient id="curve1" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style={{stopColor: '#f1f5f9', stopOpacity: 0.1}} />
                <stop offset="100%" style={{stopColor: '#e2e8f0', stopOpacity: 0.05}} />
              </linearGradient>
              <linearGradient id="curve2" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style={{stopColor: '#e2e8f0', stopOpacity: 0.08}} />
                <stop offset="100%" style={{stopColor: '#cbd5e1', stopOpacity: 0.03}} />
              </linearGradient>
            </defs>
          </svg>
        </div>

        {/* Journey Header */}
        <div className="relative z-10 px-6 pt-8">
          <div className="flex items-center gap-3">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
              <path d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2z"/>
              <path d="M8 21v-4a2 2 0 012-2h2a2 2 0 012 2v4"/>
              <path d="M9 7V4a2 2 0 012-2h0a2 2 0 012 2v3"/>
            </svg>
            <h2 className="text-white text-2xl font-medium">Journey</h2>
          </div>
        </div>

        {/* Center Card */}
        <div className="relative z-10 flex items-center justify-center min-h-[60vh] px-6">
          <div className="max-w-sm w-full">
            <div className="bg-slate-800/80 backdrop-blur-xl border border-slate-600/50 rounded-3xl p-8 shadow-2xl">
              <div className="text-center">
                <h3 className="text-white text-3xl font-serif italic leading-relaxed">
                  <div className="mb-2">Your journey</div>
                  <div className="mb-2">begins with</div>
                  <div className="mb-8">reflection.</div>
                  
                  <div className="text-2xl space-y-1">
                    <div>Add your</div>
                    <div>first</div>
                    <div>reflection to</div>
                    <div>get started.</div>
                  </div>
                </h3>
              </div>
            </div>
          </div>
        </div>

        {/* Plus Button */}
        <div className="fixed bottom-24 right-6 z-30">
          <button
            className="w-16 h-16 bg-slate-800 border-2 border-white rounded-full flex items-center justify-center shadow-2xl hover:scale-105 transition-transform duration-200"
            onClick={() => setUploadModalOpen(true)}
          >
            <Plus className="w-8 h-8 text-white" strokeWidth={2} />
          </button>
        </div>
      </div>

      {/* Bottom Navigation */}
      <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 z-20">
        <div className="flex items-center justify-around py-3 px-4">
          <div className="flex flex-col items-center">
            <div className="w-12 h-12 bg-slate-800 rounded-full flex items-center justify-center mb-1">
              <span className="text-white font-bold text-lg">N</span>
            </div>
            <span className="text-slate-800 text-sm font-medium">Journey</span>
          </div>
          <div className="flex flex-col items-center">
            <div className="text-gray-400 mb-1">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="3"/>
                <path d="M12 2v4m0 12v4M4.93 4.93l2.83 2.83m8.48 8.48l2.83 2.83M2 12h4m12 0h4M4.93 19.07l2.83-2.83m8.48-8.48l2.83-2.83"/>
              </svg>
            </div>
            <span className="text-gray-400 text-sm">Center</span>
          </div>
          <div className="flex flex-col items-center">
            <div className="text-gray-400 mb-1">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                <circle cx="9" cy="7" r="4"/>
                <path d="M23 21v-2a4 4 0 0 0-3-3.87m-4-12a4 4 0 0 1 0 7.75"/>
              </svg>
            </div>
            <span className="text-gray-400 text-sm">Coaching</span>
          </div>
        </div>
      </div>
    </div>
  );
}