'use client';

import { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { formatDistanceToNow, format } from 'date-fns';
import { useEntryService, Entry } from '@/services/entryService';

interface EntryGroup {
  month: string;
  entries: Entry[];
}

export function JourneyTab() {
  const router = useRouter();
  const entryService = useEntryService();
  const [entries, setEntries] = useState<Entry[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [offset, setOffset] = useState(0);

  useEffect(() => {
    fetchEntries(0, true);
  }, []);

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

  const getTypeLabel = (type: string) => {
    return type === 'fresh_thought' ? 'Fresh Thought' : 'Session';
  };

  const getTypeColor = (type: string) => {
    return type === 'fresh_thought' ? 'bg-green-100 text-green-800' : 'bg-muted text-muted-foreground';
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
      <div className="text-center py-12">
        <div className="text-6xl mb-4">🗺️</div>
        <h3 className="text-xl font-semibold text-gray-900 mb-2">Your Journey Starts Here</h3>
        <p className="text-gray-600 mb-6">
          Add your first entry to begin tracking your progress over time.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="relative">
        {/* Timeline Line */}
        <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-gray-200"></div>
        
        <div className="space-y-8">
          {groupedEntries.map((group, groupIndex) => (
            <div key={groupIndex}>
              {/* Month Header */}
              <div className="relative flex items-center mb-6">
                <div className="absolute left-6 w-4 h-4 bg-primary rounded-full border-4 border-white shadow-lg"></div>
                <div className="ml-16">
                  <h3 className="text-lg font-semibold text-gray-800">{group.month}</h3>
                </div>
              </div>
              
              {/* Entries for this month */}
              <div className="space-y-4">
                {group.entries.map((entry) => (
                  <div key={entry.id} className="relative">
                    <div className="absolute left-7 w-2 h-2 bg-gray-400 rounded-full"></div>
                    <div className="ml-16">
                      <Card
                        className="hover:shadow-md transition-shadow md:min-h-auto sm:min-h-[120px] cursor-pointer hover:bg-gray-50"
                        onClick={() => handleCardClick(entry)}
                      >
                        <CardHeader className="pb-3 md:pb-3 sm:pb-2">
                          {/* Desktop Layout */}
                          <div className="hidden md:flex items-center justify-between">
                            <CardTitle className="text-lg">{entry.title}</CardTitle>
                            <div className="flex items-center gap-2">
                              <Badge className={getTypeColor(entry.entry_type)}>
                                {getTypeLabel(entry.entry_type)}
                              </Badge>
                              <span className="text-sm text-gray-500">
                                {formatDistanceToNow(new Date(entry.created_at), { addSuffix: true })}
                              </span>
                            </div>
                          </div>
                          
                          {/* Mobile Layout */}
                          <div className="md:hidden">
                            <CardTitle className="text-lg w-full mb-2">{entry.title}</CardTitle>
                            <div className="flex items-center gap-2 flex-wrap">
                              <Badge className={`${getTypeColor(entry.entry_type)} text-xs`}>
                                {getTypeLabel(entry.entry_type)}
                              </Badge>
                              {entry.has_insights && (
                                <Badge variant="outline" className="text-xs">
                                  ✨ Insights
                                </Badge>
                              )}
                              <span className="text-xs text-gray-500">
                                {formatDistanceToNow(new Date(entry.created_at), { addSuffix: true })}
                              </span>
                            </div>
                          </div>
                        </CardHeader>
                        <CardContent className="md:block hidden">
                          {entry.content && (
                            <p className="text-gray-700 mb-4 line-clamp-3">{entry.content}</p>
                          )}
                          
                          {entry.has_insights && (
                            <div className="mt-4">
                              <Badge variant="outline" className="text-xs">
                                ✨ Has Insights
                              </Badge>
                            </div>
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

      {/* Floating Add Button */}
      <div className="fixed bottom-6 right-6 z-10">
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