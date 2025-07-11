"use client";

import { DashboardWidget } from './DashboardWidget';
import { Button } from '@/components/ui/button';
import { Plus, Upload, Target, Brain, Users, FileText } from 'lucide-react';
import { useRouter } from 'next/navigation';

interface QuickActionsWidgetProps {
  userRole: 'coach' | 'client';
  maxActions?: number;
  className?: string;
}

export function QuickActionsWidget({ userRole, maxActions = 6, className }: QuickActionsWidgetProps) {
  const router = useRouter();

  const coachActions = [
    {
      label: 'New Session Insight',
      icon: Brain,
      href: '/insights',
      description: 'Analyze a coaching session',
      color: 'text-purple-600'
    },
    {
      label: 'View Clients',
      icon: Users,
      href: '/connections',
      description: 'Manage client relationships',
      color: 'text-blue-600'
    },
    {
      label: 'Upload Document',
      icon: Upload,
      href: '/documents/upload',
      description: 'Add client documents',
      color: 'text-green-600'
    },
    {
      label: 'View Documents',
      icon: FileText,
      href: '/documents',
      description: 'Browse uploaded files',
      color: 'text-orange-600'
    }
  ];

  const clientActions = [
    {
      label: 'Set New Goal',
      icon: Target,
      href: '/goals',
      description: 'Create a new goal',
      color: 'text-red-600'
    },
    {
      label: 'Upload Document',
      icon: Upload,
      href: '/documents/upload',
      description: 'Share documents with coach',
      color: 'text-green-600'
    },
    {
      label: 'View Insights',
      icon: Brain,
      href: '/insights',
      description: 'Review session insights',
      color: 'text-purple-600'
    },
    {
      label: 'View Documents',
      icon: FileText,
      href: '/documents',
      description: 'Browse your files',
      color: 'text-orange-600'
    }
  ];

  const actions = (userRole === 'coach' ? coachActions : clientActions).slice(0, maxActions);

  return (
    <DashboardWidget
      title="Quick Actions"
      description="Common tasks and shortcuts"
      icon={Plus}
      className={className}
    >
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {actions.map((action, index) => (
          <Button
            key={index}
            variant="outline"
            className="h-auto p-4 flex flex-col items-center space-y-2 hover:bg-accent/50 transition-colors"
            onClick={() => router.push(action.href)}
          >
            <action.icon className={`h-6 w-6 ${action.color}`} />
            <div className="text-center">
              <div className="font-medium text-sm">{action.label}</div>
              <div className="text-xs text-muted-foreground">{action.description}</div>
            </div>
          </Button>
        ))}
      </div>
    </DashboardWidget>
  );
}