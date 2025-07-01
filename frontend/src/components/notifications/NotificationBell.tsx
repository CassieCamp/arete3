"use client";

import { useState, useEffect } from 'react';
import { useAuth } from '@/context/AuthContext';
import { notificationService } from '@/services/notificationService';
import { NotificationCenter } from './NotificationCenter';
import { useWebSocket } from '@/hooks/useWebSocket';
import { Button } from '@/components/ui/button';
import { Bell } from 'lucide-react';

export function NotificationBell() {
  const { getAuthToken, isAuthenticated } = useAuth();
  const [unreadCount, setUnreadCount] = useState(0);
  const [isNotificationCenterOpen, setIsNotificationCenterOpen] = useState(false);
  const [loading, setLoading] = useState(false);

  // Set up WebSocket for real-time notifications
  useWebSocket({
    onMessage: (message) => {
      if (message.type === 'notification') {
        // New notification received, update unread count
        fetchUnreadCount();
      }
    },
    onConnect: () => {
      console.log('Notification WebSocket connected');
    },
    onDisconnect: () => {
      console.log('Notification WebSocket disconnected');
    }
  });

  useEffect(() => {
    if (isAuthenticated) {
      fetchUnreadCount();
      // Set up polling for unread count every 60 seconds as backup
      const interval = setInterval(fetchUnreadCount, 60000);
      return () => clearInterval(interval);
    }
  }, [isAuthenticated]);

  const fetchUnreadCount = async () => {
    try {
      setLoading(true);
      const token = await getAuthToken();
      if (!token) return;

      const count = await notificationService.getUnreadCount(token);
      setUnreadCount(count);
    } catch (err) {
      console.error('Error fetching unread count:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleBellClick = () => {
    setIsNotificationCenterOpen(true);
  };

  const handleNotificationCenterClose = () => {
    setIsNotificationCenterOpen(false);
    // Refresh unread count when notification center closes
    fetchUnreadCount();
  };

  if (!isAuthenticated) {
    return null;
  }

  return (
    <>
      <Button
        variant="ghost"
        size="sm"
        onClick={handleBellClick}
        className="relative p-2 text-gray-600 hover:text-gray-900"
        disabled={loading}
      >
        <Bell className="h-5 w-5" />
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center min-w-[20px]">
            {unreadCount > 99 ? '99+' : unreadCount}
          </span>
        )}
      </Button>

      <NotificationCenter
        isOpen={isNotificationCenterOpen}
        onClose={handleNotificationCenterClose}
      />
    </>
  );
}