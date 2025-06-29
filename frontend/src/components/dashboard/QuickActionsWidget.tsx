"use client";

import React from 'react';
import Link from 'next/link';
import { DashboardWidget } from './DashboardWidget';
import { Button } from '@/components/ui/button';
import { 
  Users, 
  FileText, 
  Target, 
  Brain, 
  Plus, 
  Calendar,
  MessageSquare,
  BarChart3,
  Settings,
  UserPlus,
  Upload,
  LucideIcon
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface QuickAction {
  id: string;
  title: string;
  description: string;
  href: string;
  icon: LucideIcon;
  color: string;
  roles: ('coach' | 'client')[];
  priority: number;
}

const quickActions: QuickAction[] = [
  // Coach-specific actions
  {
    id: 'manage-clients',
    title: 'Manage Clients',
    description: 'View and manage your coaching relationships',
    href: '/dashboard/connections',
    icon: Users,
    color: 'bg-blue-500 hover:bg-blue-600',
    roles: ['coach'],
    priority: 1
  },
  {
    id: 'schedule-session',
    title: 'Schedule Session',
    description: 'Book a new coaching session',
    href: '/dashboard/sessions/schedule',
    icon: Calendar,
    color: 'bg-purple-500 hover:bg-purple-600',
    roles: ['coach'],
    priority: 2
  },
  {
    id: 'client-insights',
    title: 'Client Insights',
    description: 'Review AI-powered client insights',
    href: '/dashboard/insights',
    icon: Brain,
    color: 'bg-orange-500 hover:bg-orange-600',
    roles: ['coach'],
    priority: 3
  },
  {
    id: 'invite-client',
    title: 'Invite Client',
    description: 'Send invitation to new client',
    href: '/dashboard/connections?action=invite',
    icon: UserPlus,
    color: 'bg-green-500 hover:bg-green-600',
    roles: ['coach'],
    priority: 4
  },

  // Client-specific actions
  {
    id: 'view-goals',
    title: 'My Goals',
    description: 'Track your personal development goals',
    href: '/dashboard/goals',
    icon: Target,
    color: 'bg-purple-500 hover:bg-purple-600',
    roles: ['client'],
    priority: 1
  },
  {
    id: 'upload-documents',
    title: 'Upload Documents',
    description: 'Add documents for analysis',
    href: '/dashboard/documents/upload',
    icon: Upload,
    color: 'bg-green-500 hover:bg-green-600',
    roles: ['client'],
    priority: 2
  },
  {
    id: 'view-insights',
    title: 'My Insights',
    description: 'Explore your session insights',
    href: '/dashboard/insights',
    icon: Brain,
    color: 'bg-orange-500 hover:bg-orange-600',
    roles: ['client'],
    priority: 3
  },
  {
    id: 'message-coach',
    title: 'Message Coach',
    description: 'Connect with your coach',
    href: '/dashboard/connections',
    icon: MessageSquare,
    color: 'bg-blue-500 hover:bg-blue-600',
    roles: ['client'],
    priority: 4
  },

  // Shared actions
  {
    id: 'view-progress',
    title: 'View Progress',
    description: 'Track your coaching journey',
    href: '/dashboard/progress',
    icon: BarChart3,
    color: 'bg-indigo-500 hover:bg-indigo-600',
    roles: ['coach', 'client'],
    priority: 5
  },
  {
    id: 'settings',
    title: 'Settings',
    description: 'Manage your account preferences',
    href: '/dashboard/settings',
    icon: Settings,
    color: 'bg-gray-500 hover:bg-gray-600',
    roles: ['coach', 'client'],
    priority: 6
  }
];

interface QuickActionsWidgetProps {
  userRole: 'coach' | 'client';
  maxActions?: number;
  layout?: 'grid' | 'list';
  showAll?: boolean;
  className?: string;
}

export function QuickActionsWidget({
  userRole,
  maxActions = 4,
  layout = 'grid',
  showAll = false,
  className
}: QuickActionsWidgetProps) {
  // Filter actions based on user role and priority
  const filteredActions = quickActions
    .filter(action => action.roles.includes(userRole))
    .sort((a, b) => a.priority - b.priority)
    .slice(0, showAll ? undefined : maxActions);

  const handleRefresh = () => {
    // In a real implementation, this might refresh user-specific quick actions
    window.location.reload();
  };

  return (
    <DashboardWidget
      title="Quick Actions"
      description={`${userRole === 'coach' ? 'Coach' : 'Client'} shortcuts`}
      icon={Plus}
      onRefresh={handleRefresh}
      size="lg"
      className={className}
    >
      <div className={cn(
        layout === 'grid' 
          ? "grid grid-cols-1 sm:grid-cols-2 gap-3"
          : "space-y-2"
      )}>
        {filteredActions.map((action) => (
          <QuickActionCard
            key={action.id}
            action={action}
            layout={layout}
          />
        ))}
      </div>
      
      {!showAll && quickActions.filter(a => a.roles.includes(userRole)).length > maxActions && (
        <div className="mt-4 pt-4 border-t">
          <Button variant="outline" size="sm" className="w-full">
            <Plus className="h-4 w-4 mr-2" />
            View All Actions
          </Button>
        </div>
      )}
    </DashboardWidget>
  );
}

interface QuickActionCardProps {
  action: QuickAction;
  layout: 'grid' | 'list';
}

function QuickActionCard({ action, layout }: QuickActionCardProps) {
  const Icon = action.icon;

  if (layout === 'list') {
    return (
      <Link href={action.href}>
        <div className="flex items-center space-x-3 p-3 rounded-lg border hover:bg-accent transition-colors cursor-pointer">
          <div className={cn("p-2 rounded-lg text-white", action.color)}>
            <Icon className="h-4 w-4" />
          </div>
          <div className="flex-1 min-w-0">
            <h4 className="font-medium text-sm">{action.title}</h4>
            <p className="text-xs text-muted-foreground truncate">
              {action.description}
            </p>
          </div>
        </div>
      </Link>
    );
  }

  return (
    <Link href={action.href}>
      <div className="group p-4 rounded-lg border hover:shadow-md transition-all cursor-pointer hover:border-primary/20">
        <div className="flex items-start space-x-3">
          <div className={cn(
            "p-2 rounded-lg text-white transition-colors",
            action.color
          )}>
            <Icon className="h-5 w-5" />
          </div>
          <div className="flex-1 min-w-0">
            <h4 className="font-medium text-sm group-hover:text-primary transition-colors">
              {action.title}
            </h4>
            <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
              {action.description}
            </p>
          </div>
        </div>
      </div>
    </Link>
  );
}

// Compact version for smaller spaces
export function QuickActionsCompact({
  userRole,
  maxActions = 3
}: {
  userRole: 'coach' | 'client';
  maxActions?: number;
}) {
  const filteredActions = quickActions
    .filter(action => action.roles.includes(userRole))
    .sort((a, b) => a.priority - b.priority)
    .slice(0, maxActions);

  return (
    <div className="space-y-2">
      {filteredActions.map((action) => {
        const Icon = action.icon;
        return (
          <Link key={action.id} href={action.href}>
            <Button 
              variant="ghost" 
              className="w-full justify-start h-auto p-3"
            >
              <div className={cn("p-1.5 rounded text-white mr-3", action.color)}>
                <Icon className="h-3 w-3" />
              </div>
              <div className="text-left">
                <div className="font-medium text-sm">{action.title}</div>
                <div className="text-xs text-muted-foreground">
                  {action.description}
                </div>
              </div>
            </Button>
          </Link>
        );
      })}
    </div>
  );
}