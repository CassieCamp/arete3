"use client";

import { QuoteCarousel } from '@/components/quotes/QuoteCarousel';
import { BottomNavigation } from '@/components/navigation/BottomNavigation';
import { UnifiedEntryCTA } from '@/components/entries/UnifiedEntryCTA';
import { FreemiumStatus } from '@/services/entryService';

// Mock data for demo purposes
const mockFreemiumStatus: FreemiumStatus = {
  has_coach: false,
  entries_count: 0,
  max_free_entries: 5,
  entries_remaining: 3,
  can_create_entries: true,
  can_access_insights: false,
  is_freemium: true
};

export default function DemoLandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white dark:from-slate-900 dark:to-slate-800 pb-20">
      {/* Welcome Section */}
      <div className="pt-8 pb-4 px-4">
        <div className="max-w-md mx-auto text-center">
          <h1 className="text-2xl font-bold text-foreground mb-2">
            Welcome back, Demo User!
          </h1>
          <p className="text-muted-foreground">
            Continue your growth journey with personalized coaching.
          </p>
        </div>
      </div>

      {/* Quote Carousel Section */}
      <div className="px-4 mb-8">
        <div className="w-full max-w-md mx-auto">
          {/* Demo Quote Carousel with fallback data */}
          <div className="bg-card rounded-lg border p-8">
            <div className="text-center mb-6">
              <blockquote className="text-lg font-medium text-foreground mb-4 leading-relaxed">
                "The only way to do great work is to love what you do."
              </blockquote>
              <cite className="text-sm text-muted-foreground">
                — Steve Jobs
              </cite>
            </div>
            
            {/* Heart Button */}
            <div className="flex justify-center mb-6">
              <button className="p-3 rounded-full transition-all duration-200 text-muted-foreground hover:text-red-500 hover:scale-110">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                </svg>
              </button>
            </div>
            
            {/* Navigation dots */}
            <div className="flex justify-center space-x-2">
              <div className="w-2 h-2 rounded-full bg-primary"></div>
              <div className="w-2 h-2 rounded-full bg-muted-foreground/30"></div>
              <div className="w-2 h-2 rounded-full bg-muted-foreground/30"></div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Main Content Area */}
      <div className="px-4 space-y-6">
        {/* Entry Creation CTA */}
        <UnifiedEntryCTA
          freemiumStatus={mockFreemiumStatus}
        />

        {/* Additional Content Sections */}
        <div className="space-y-4">
          {/* Quick Stats */}
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-card rounded-lg p-4 border">
              <div className="text-2xl font-bold text-primary">3</div>
              <div className="text-sm text-muted-foreground">Entries remaining</div>
            </div>
            <div className="bg-card rounded-lg p-4 border">
              <div className="text-2xl font-bold text-primary">1</div>
              <div className="text-sm text-muted-foreground">Coach connection</div>
            </div>
          </div>

          {/* Recent Activity Preview */}
          <div className="bg-card rounded-lg p-4 border">
            <h3 className="font-semibold mb-3">Recent Activity</h3>
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Last entry</span>
                <span className="text-foreground">2 days ago</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Goal progress</span>
                <span className="text-foreground">Updated yesterday</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Next session</span>
                <span className="text-foreground">Tomorrow 2:00 PM</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Bottom Navigation */}
      <BottomNavigation
        activeTab="mountain"
      />
    </div>
  );
}