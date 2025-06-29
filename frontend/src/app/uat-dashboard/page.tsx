'use client'

import React, { useState } from 'react'
import { DashboardWidget } from '@/components/dashboard/DashboardWidget'
import { QuickActionsWidget } from '@/components/dashboard/QuickActionsWidget'
import { ProgressOverviewWidget } from '@/components/dashboard/ProgressOverviewWidget'

// Mock user data for UAT testing
type MockUser = {
  id: string;
  role: 'coach' | 'client';
  name: string;
  email: string;
}

const mockClientUser: MockUser = {
  id: 'uat-client-1',
  role: 'client',
  name: 'UAT Test Client',
  email: 'uat-client@example.com'
}

const mockCoachUser: MockUser = {
  id: 'uat-coach-1',
  role: 'coach',
  name: 'UAT Test Coach',
  email: 'uat-coach@example.com'
}

export default function UATDashboardPage() {
  // Toggle between client and coach views for testing
  const [currentUser, setCurrentUser] = useState<MockUser>(mockClientUser)
  const [isLoading, setIsLoading] = useState(false)
  const [hasError, setHasError] = useState(false)

  return (
    <div className="min-h-screen bg-gray-50">
      {/* UAT Controls */}
      <div className="bg-yellow-100 border-b border-yellow-200 p-4">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-lg font-semibold text-yellow-800 mb-2">
            🧪 UAT Dashboard Testing Environment
          </h1>
          <div className="flex gap-4 items-center">
            <button
              onClick={() => setCurrentUser(mockClientUser)}
              className={`px-3 py-1 rounded text-sm ${
                currentUser.role === 'client' 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-white text-gray-700 border'
              }`}
            >
              Test as Client
            </button>
            <button
              onClick={() => setCurrentUser(mockCoachUser)}
              className={`px-3 py-1 rounded text-sm ${
                currentUser.role === 'coach' 
                  ? 'bg-green-600 text-white' 
                  : 'bg-white text-gray-700 border'
              }`}
            >
              Test as Coach
            </button>
            <button
              onClick={() => setIsLoading(!isLoading)}
              className="px-3 py-1 rounded text-sm bg-orange-600 text-white"
            >
              Toggle Loading: {isLoading ? 'ON' : 'OFF'}
            </button>
            <button
              onClick={() => setHasError(!hasError)}
              className="px-3 py-1 rounded text-sm bg-red-600 text-white"
            >
              Toggle Error: {hasError ? 'ON' : 'OFF'}
            </button>
          </div>
        </div>
      </div>

      {/* Dashboard Header */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                Welcome back, {currentUser.name}
              </h1>
              <p className="text-gray-600">
                Role: {currentUser.role.charAt(0).toUpperCase() + currentUser.role.slice(1)}
              </p>
            </div>
            <div className="text-sm text-gray-500">
              Sprint S8 - Enhanced Dashboard
            </div>
          </div>
        </div>
      </div>

      {/* Dashboard Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Quick Actions Widget */}
          <div className="lg:col-span-1">
            <QuickActionsWidget
              userRole={currentUser.role}
            />
          </div>

          {/* Progress Overview Widget */}
          <div className="lg:col-span-2">
            <ProgressOverviewWidget
              userRole={currentUser.role}
            />
          </div>

          {/* Additional Test Widgets */}
          <div className="lg:col-span-1">
            <DashboardWidget
              title="Test Widget - Small"
              size="sm"
              loading={isLoading}
              error={hasError ? 'Test error state' : undefined}
            >
              <div className="p-4">
                <p className="text-sm text-gray-600">
                  Small widget content for testing responsive layout.
                </p>
              </div>
            </DashboardWidget>
          </div>

          <div className="lg:col-span-2">
            <DashboardWidget
              title="Test Widget - Large"
              size="lg"
              loading={isLoading}
              error={hasError ? 'Test error state' : undefined}
            >
              <div className="p-6">
                <p className="text-gray-600 mb-4">
                  Large widget content demonstrating the widget framework capabilities:
                </p>
                <ul className="list-disc list-inside space-y-2 text-sm text-gray-600">
                  <li>Responsive grid layout</li>
                  <li>Loading state management</li>
                  <li>Error handling</li>
                  <li>Role-based content</li>
                  <li>Consistent styling</li>
                </ul>
              </div>
            </DashboardWidget>
          </div>

          <div className="lg:col-span-3">
            <DashboardWidget
              title="Test Widget - Full Width"
              size="xl"
              loading={isLoading}
              error={hasError ? 'Test error state' : undefined}
            >
              <div className="p-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="bg-blue-50 p-4 rounded">
                    <h4 className="font-medium text-blue-900">Feature 1</h4>
                    <p className="text-sm text-blue-700">Widget framework testing</p>
                  </div>
                  <div className="bg-green-50 p-4 rounded">
                    <h4 className="font-medium text-green-900">Feature 2</h4>
                    <p className="text-sm text-green-700">Role-based functionality</p>
                  </div>
                  <div className="bg-purple-50 p-4 rounded">
                    <h4 className="font-medium text-purple-900">Feature 3</h4>
                    <p className="text-sm text-purple-700">Responsive design</p>
                  </div>
                </div>
              </div>
            </DashboardWidget>
          </div>
        </div>
      </div>
    </div>
  )
}