"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { PageHeader } from "@/components/navigation/NavigationUtils";
import { useAuth } from "@/context/AuthContext";
import { Settings, User, Bell, Shield } from "lucide-react";

export default function SettingsPage() {
  const { user } = useAuth();

  const settingsCategories = [
    {
      title: 'Profile Settings',
      description: 'Manage your personal information and preferences',
      icon: User,
      href: '/profile/edit',
      color: 'bg-blue-500'
    },
    {
      title: 'Notifications',
      description: 'Configure your notification preferences',
      icon: Bell,
      color: 'bg-green-500',
      comingSoon: true
    },
    {
      title: 'Privacy & Security',
      description: 'Manage your privacy and security settings',
      icon: Shield,
      color: 'bg-purple-500',
      comingSoon: true
    },
    {
      title: 'Account Settings',
      description: 'Billing, subscription, and account management',
      icon: Settings,
      color: 'bg-orange-500',
      comingSoon: true
    }
  ];

  return (
    <div>
      <PageHeader />
      
      <div className="space-y-6">
        {/* User Info Card */}
        <Card>
          <CardHeader>
            <CardTitle>Account Information</CardTitle>
            <CardDescription>
              Your current account details and role
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">{user?.firstName} {user?.lastName}</p>
                  <p className="text-sm text-muted-foreground">{user?.email}</p>
                </div>
                <div className="flex items-center gap-2">
                  <div className={`w-2 h-2 rounded-full ${
                    user?.role === 'coach' ? 'bg-blue-500' : 'bg-green-500'
                  }`} />
                  <span className="text-sm font-medium capitalize">{user?.role}</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Settings Categories */}
        <div>
          <h2 className="text-lg font-semibold mb-4">Settings Categories</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {settingsCategories.map((category) => (
              <Card key={category.title} className="hover:shadow-md transition-shadow">
                <CardContent className="p-6">
                  <div className="flex items-start space-x-4">
                    <div className={`p-3 rounded-lg ${category.color}`}>
                      <category.icon className="h-6 w-6 text-white" />
                    </div>
                    <div className="flex-1">
                      <h3 className="font-medium mb-1">{category.title}</h3>
                      <p className="text-sm text-muted-foreground mb-3">
                        {category.description}
                      </p>
                      {category.comingSoon ? (
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                          Coming Soon
                        </span>
                      ) : (
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => window.location.href = category.href!}
                        >
                          Configure
                        </Button>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>
              Common settings and account actions
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <Button variant="outline" className="w-full justify-start">
                <User className="h-4 w-4 mr-2" />
                Edit Profile Information
              </Button>
              <Button variant="outline" className="w-full justify-start" disabled>
                <Bell className="h-4 w-4 mr-2" />
                Notification Preferences (Coming Soon)
              </Button>
              <Button variant="outline" className="w-full justify-start" disabled>
                <Shield className="h-4 w-4 mr-2" />
                Privacy Settings (Coming Soon)
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}