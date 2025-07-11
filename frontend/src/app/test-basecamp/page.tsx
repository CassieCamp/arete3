"use client";

import { BasecampTab } from '@/components/mountain/BasecampTab';

// Mock AuthContext for testing
const MockAuthProvider = ({ children }: { children: React.ReactNode }) => {
  const mockAuthContext = {
    getAuthToken: async () => 'mock-token',
    isAuthenticated: true,
    user: { id: 'test-user' }
  };

  return (
    <div>
      {/* Mock the auth context by providing the values directly to children */}
      {children}
    </div>
  );
};

export default function TestBasecampPage() {
  return (
    <MockAuthProvider>
      <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white dark:from-slate-900 dark:to-slate-800 pb-20">
        <div className="container mx-auto px-4 py-8">
          <div className="mb-8 text-center">
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
              Basecamp Tab Test
            </h1>
            <p className="text-gray-600 dark:text-gray-300">
              Testing the enhanced Basecamp tab with document functionality
            </p>
          </div>

          <div className="w-full max-w-4xl mx-auto">
            <BasecampTab />
          </div>
        </div>
      </div>
    </MockAuthProvider>
  );
}