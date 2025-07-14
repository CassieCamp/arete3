'use client';

import React, { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { formatDistanceToNow, format } from 'date-fns';
import { useEntryService, Entry } from '@/services/entryService';
import { useAuth } from '@/context/AuthContext';
import { FileText, MessageSquare, Lightbulb, Plus } from 'lucide-react';

interface EntryGroup {
  month: string;
  entries: Entry[];
}

export function JourneyTab() {
  const router = useRouter();
  const entryService = useEntryService();
  const { isAuthenticated, user } = useAuth();
  const [entries, setEntries] = useState<Entry[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [offset, setOffset] = useState(0);

  useEffect(() => {
    if (isAuthenticated && user) {
      fetchEntries(0, true);
    }
  }, [isAuthenticated, user]);

  const fetchEntries = async (currentOffset: number, isInitial = false) => {
    try {
      if (isInitial) {
        setLoading(true);
      } else {
        setLoadingMore(true);
      }

      const data = await entryService.getEntries({
        limit: 20,
        offset: currentOffset
      });
      const newEntries = data.entries || [];

      if (isInitial) {
        setEntries(newEntries);
      } else {
        setEntries(prev => [...prev, ...newEntries]);
      }

      setHasMore(newEntries.length === 20);
      setOffset(currentOffset + newEntries.length);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  };

  const loadMore = useCallback(() => {
    if (hasMore && !loadingMore) {
      fetchEntries(offset);
    }
  }, [hasMore, loadingMore, offset]);

  // Group entries by month
  const groupedEntries: EntryGroup[] = entries.reduce((groups: EntryGroup[], entry) => {
    const date = new Date(entry.session_date || entry.created_at);
    const monthKey = format(date, 'MMMM yyyy');
    
    let group = groups.find(g => g.month === monthKey);
    if (!group) {
      group = { month: monthKey, entries: [] };
      groups.push(group);
    }
    
    group.entries.push(entry);
    return groups;
  }, []);

  const getTypeLabel = (entry: Entry) => {
    if (entry.transcript_source === 'file_upload') {
      return 'Document Insight';
    }
    return entry.entry_type === 'fresh_thought' ? 'Fresh Thought' : 'Session';
  };

  const getTypeColor = (entry: Entry) => {
    if (entry.transcript_source === 'file_upload') {
      return 'bg-blue-100 text-blue-800';
    }
    return entry.entry_type === 'fresh_thought' ? 'bg-green-100 text-green-800' : 'bg-muted text-muted-foreground';
  };

  const getTypeIcon = (entry: Entry) => {
    if (entry.transcript_source === 'file_upload') {
      return FileText;
    }
    return entry.entry_type === 'fresh_thought' ? Lightbulb : MessageSquare;
  };

  const handleCardClick = (entry: Entry) => {
    router.push(`/insights/${entry.id}`);
  };

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto"></div>
          <p className="mt-2 text-gray-600">Loading your journey...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <p className="text-red-600">Error loading journey: {error}</p>
      </div>
    );
  }

  if (entries.length === 0) {
    return (
      <>
        <div className="flex items-center justify-center min-h-[60vh]">
          <div className="relative">
            <div
              className="absolute inset-0 rounded-3xl"
              style={{
                backgroundImage: 'linear-gradient(135deg, rgba(0, 0, 0, 0.25) 0%, rgba(0, 0, 0, 0.15) 30%, rgba(0, 0, 0, 0.08) 60%, transparent 100%)'
              }}
            />
            <p className="relative text-4xl italic font-serif text-primary-foreground text-center px-8 py-6">
              The first step of your journey is to add a reflection.
            </p>
          </div>
        </div>

        {/* Fixed Add Button - positioned above bottom navigation with animation for empty state */}
        <div className="fixed bottom-20 right-6 z-10">
          <div
            className="rounded-full w-14 h-14 bg-primary text-primary-foreground shadow-lg hover:shadow-xl transition-all cursor-pointer flex items-center justify-center"
            onClick={() => router.push('/documents/upload')}
            role="button"
            tabIndex={0}
            aria-label="Add new entry"
            style={{
              animation: 'glowPulse 4s ease-in-out infinite, scalePulse 3s ease-in-out infinite'
            }}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                router.push('/documents/upload');
              }
            }}
          >
            <span className="text-2xl">+</span>
          </div>
        </div>
        
        {/* CSS animations using style tag */}
        <style jsx>{`
          @keyframes glowPulse {
            0%, 100% {
              box-shadow: 0 4px 14px 0 rgba(0, 0, 0, 0.1), 0 0 16px 4px oklch(0.9583 0.0111 89.7230 / 0.4);
            }
            50% {
              box-shadow: 0 4px 14px 0 rgba(0, 0, 0, 0.1), 0 0 24px 8px oklch(0.9583 0.0111 89.7230 / 0.6);
            }
          }
          
          @keyframes scalePulse {
            0%, 100% {
              transform: scale(1);
              opacity: 0.9;
            }
            50% {
              transform: scale(1.05);
              opacity: 1;
            }
          }
        `}</style>
      </>
    );
  }

  return (
    <div className="w-full">
      {/* Timeline Content */}
      <div className="w-full">
        <div className="pt-2">
          <div className="space-y-6">
            {groupedEntries.map((group, groupIndex) => (
              <div key={groupIndex}>
                {/* Entries for this month - removed month header */}
                <div className="space-y-4">
                  {group.entries.map((entry) => (
                    <div key={entry.id}>
                      <div>
                        <Card
                          className="hover:shadow-md transition-shadow md:min-h-auto sm:min-h-[120px] cursor-pointer hover:bg-gray-50 md:max-w-4xl md:mx-auto"
                          onClick={() => handleCardClick(entry)}
                        >
                          <CardHeader className="pb-3 md:pb-3 sm:pb-2">
                            {/* Desktop Layout */}
                            <div className="hidden md:block">
                              <div className="flex items-start gap-2 mb-2">
                                {React.createElement(getTypeIcon(entry), {
                                  className: "w-5 h-5 mt-0.5 text-gray-600 flex-shrink-0"
                                })}
                                <CardTitle className="text-lg">{entry.title}</CardTitle>
                              </div>
                              <div className="flex items-center gap-2">
                                <Badge className={getTypeColor(entry)}>
                                  {getTypeLabel(entry)}
                                </Badge>
                                <span className="text-sm text-gray-500">
                                  {format(new Date(entry.created_at), 'MMM d, yyyy')}
                                </span>
                              </div>
                            </div>
                            
                            {/* Mobile Layout */}
                            <div className="md:hidden">
                              <div className="flex items-start gap-2 mb-2">
                                {React.createElement(getTypeIcon(entry), {
                                  className: "w-4 h-4 mt-1 text-gray-600 flex-shrink-0"
                                })}
                                <CardTitle className="text-lg w-full">{entry.title}</CardTitle>
                              </div>
                              <div className="flex items-center gap-2 flex-wrap">
                                <Badge className={`${getTypeColor(entry)} text-xs`}>
                                  {getTypeLabel(entry)}
                                </Badge>
                                <span className="text-xs text-gray-500">
                                  {format(new Date(entry.created_at), 'MMM d, yyyy')}
                                </span>
                              </div>
                            </div>
                          </CardHeader>
                          <CardContent className="md:block hidden">
                            {entry.content && (
                              <p className="text-gray-700 mb-4 line-clamp-3">{entry.content}</p>
                            )}
                          </CardContent>
                        </Card>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
          
          {/* Load More Button */}
          {hasMore && (
            <div className="text-center mt-8">
              <button
                onClick={loadMore}
                disabled={loadingMore}
                className="bg-gray-200 text-gray-700 px-6 py-3 rounded-lg hover:bg-gray-300 disabled:opacity-50 transition-colors"
              >
                {loadingMore ? 'Loading...' : 'Load More'}
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Fixed Add Button - positioned above bottom navigation */}
      <div className="fixed bottom-20 right-6 z-10">
        <Button
          onClick={() => router.push('/documents/upload')}
          className="rounded-full w-14 h-14 shadow-lg hover:shadow-xl transition-all bg-primary text-primary-foreground"
          aria-label="Add new entry"
        >
          <span className="text-2xl">+</span>
        </Button>
      </div>
    </div>
  );
}