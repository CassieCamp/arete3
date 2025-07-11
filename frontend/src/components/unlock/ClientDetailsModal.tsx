'use client';

import { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { X, User, FileText, BookOpen, Calendar, TrendingUp } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';

interface CoachClient {
  id: string;
  name: string;
  email: string;
  relationship_status: string;
  entries_count: number;
  last_entry_date: string | null;
  created_at: string;
}

interface ClientNotes {
  note_of_moment: string;
  way_of_working: string;
  about_me: string;
}

interface ClientEntry {
  id: string;
  title: string;
  content: string;
  entry_type: string;
  created_at: string;
}

interface ClientDestination {
  id: string;
  title: string;
  description: string;
  status: string;
  created_at: string;
}

interface ClientDetailsModalProps {
  client: CoachClient;
  isOpen: boolean;
  onClose: () => void;
  onUpdate: () => void;
}

export function ClientDetailsModal({ client, isOpen, onClose, onUpdate }: ClientDetailsModalProps) {
  const { getAuthToken } = useAuth();
  const [clientNotes, setClientNotes] = useState<ClientNotes>({
    note_of_moment: '',
    way_of_working: '',
    about_me: ''
  });
  const [recentEntries, setRecentEntries] = useState<ClientEntry[]>([]);
  const [destinations, setDestinations] = useState<ClientDestination[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [activeTab, setActiveTab] = useState<'overview' | 'notes' | 'insights'>('overview');
  const [hasChanges, setHasChanges] = useState(false);

  useEffect(() => {
    if (isOpen && client) {
      loadClientData();
    }
  }, [isOpen, client]);

  const loadClientData = async () => {
    try {
      setIsLoading(true);
      const token = await getAuthToken();
      if (!token) throw new Error('No authentication token');

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      
      const [notesResponse, insightsResponse] = await Promise.all([
        fetch(`${apiUrl}/api/v1/unlock/clients/${client.id}/notes`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }),
        fetch(`${apiUrl}/api/v1/unlock/clients/${client.id}/insights`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        })
      ]);

      if (notesResponse.ok) {
        const notesData = await notesResponse.json();
        setClientNotes(notesData.notes || {
          note_of_moment: '',
          way_of_working: '',
          about_me: ''
        });
      }

      if (insightsResponse.ok) {
        const insightsData = await insightsResponse.json();
        setRecentEntries(insightsData.recent_entries || []);
        setDestinations(insightsData.destinations || []);
      }
    } catch (error) {
      console.error('Failed to load client data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const saveClientNotes = async () => {
    try {
      setIsSaving(true);
      const token = await getAuthToken();
      if (!token) throw new Error('No authentication token');

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/v1/unlock/clients/${client.id}/notes`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(clientNotes)
      });

      if (!response.ok) {
        throw new Error('Failed to save notes');
      }

      setHasChanges(false);
      onUpdate();
    } catch (error) {
      console.error('Failed to save client notes:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const handleNotesChange = (field: keyof ClientNotes, value: string) => {
    setClientNotes(prev => ({ ...prev, [field]: value }));
    setHasChanges(true);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const getEntryTypeColor = (type: string) => {
    switch (type) {
      case 'session':
        return 'bg-blue-100 text-blue-800';
      case 'thought':
        return 'bg-green-100 text-green-800';
      case 'reflection':
        return 'bg-purple-100 text-purple-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (!isOpen) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-hidden">
        <DialogHeader>
          <div className="flex items-center justify-between">
            <div>
              <DialogTitle className="text-xl font-semibold">{client.name}</DialogTitle>
              <p className="text-gray-600 mt-1">{client.email}</p>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={onClose}
              className="h-8 w-8 p-0"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        </DialogHeader>

        <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as any)} className="flex-1">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="overview" className="flex items-center gap-2">
              <User className="w-4 h-4" />
              Overview
            </TabsTrigger>
            <TabsTrigger value="notes" className="flex items-center gap-2">
              <FileText className="w-4 h-4" />
              Notes
            </TabsTrigger>
            <TabsTrigger value="insights" className="flex items-center gap-2">
              <TrendingUp className="w-4 h-4" />
              Insights
            </TabsTrigger>
          </TabsList>

          <div className="mt-6 overflow-y-auto max-h-[60vh]">
            <TabsContent value="overview" className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <FileText className="w-5 h-5" />
                      Activity Summary
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Total Entries</span>
                      <span className="font-semibold">{client.entries_count}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Last Entry</span>
                      <span className="font-semibold">
                        {client.last_entry_date ? formatDate(client.last_entry_date) : 'Never'}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Client Since</span>
                      <span className="font-semibold">{formatDate(client.created_at)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Status</span>
                      <Badge className="bg-green-100 text-green-800">
                        {client.relationship_status}
                      </Badge>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <BookOpen className="w-5 h-5" />
                      Goals & Progress
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div className="text-sm text-gray-600">
                        Active Destinations: {destinations.length}
                      </div>
                      {destinations.slice(0, 3).map((destination) => (
                        <div key={destination.id} className="p-3 bg-gray-50 rounded-lg">
                          <div className="font-medium text-sm">{destination.title}</div>
                          <div className="text-xs text-gray-600 mt-1">
                            {destination.description.substring(0, 100)}...
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            <TabsContent value="notes" className="space-y-6">
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-semibold">Client-Specific Content</h3>
                {hasChanges && (
                  <Button
                    onClick={saveClientNotes}
                    disabled={isSaving}
                    className="bg-blue-600 text-white hover:bg-blue-700"
                  >
                    {isSaving ? 'Saving...' : 'Save Changes'}
                  </Button>
                )}
              </div>

              <div className="space-y-6">
                <div>
                  <Label htmlFor="note_of_moment" className="text-sm font-medium">
                    Note of the Moment
                  </Label>
                  <p className="text-xs text-gray-500 mb-2">
                    A current message or encouragement for this client
                  </p>
                  <Textarea
                    id="note_of_moment"
                    value={clientNotes.note_of_moment}
                    onChange={(e) => handleNotesChange('note_of_moment', e.target.value)}
                    placeholder="e.g., 'Great progress on your leadership goals this week!'"
                    className="min-h-[80px]"
                  />
                </div>

                <div>
                  <Label htmlFor="way_of_working" className="text-sm font-medium">
                    Way of Working
                  </Label>
                  <p className="text-xs text-gray-500 mb-2">
                    Your coaching approach for this specific client
                  </p>
                  <Textarea
                    id="way_of_working"
                    value={clientNotes.way_of_working}
                    onChange={(e) => handleNotesChange('way_of_working', e.target.value)}
                    placeholder="e.g., 'I focus on strengths-based coaching with weekly check-ins...'"
                    className="min-h-[120px]"
                  />
                </div>

                <div>
                  <Label htmlFor="about_me" className="text-sm font-medium">
                    About Me (for this client)
                  </Label>
                  <p className="text-xs text-gray-500 mb-2">
                    Personalized introduction relevant to this client
                  </p>
                  <Textarea
                    id="about_me"
                    value={clientNotes.about_me}
                    onChange={(e) => handleNotesChange('about_me', e.target.value)}
                    placeholder="e.g., 'As someone who has also navigated leadership transitions...'"
                    className="min-h-[120px]"
                  />
                </div>
              </div>
            </TabsContent>

            <TabsContent value="insights" className="space-y-6">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Recent Entries</CardTitle>
                    <CardDescription>
                      Latest entries from your client
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    {recentEntries.length === 0 ? (
                      <p className="text-gray-500 text-sm">No entries yet</p>
                    ) : (
                      <div className="space-y-3">
                        {recentEntries.map((entry) => (
                          <div key={entry.id} className="p-3 border rounded-lg">
                            <div className="flex items-center justify-between mb-2">
                              <Badge className={getEntryTypeColor(entry.entry_type)}>
                                {entry.entry_type}
                              </Badge>
                              <span className="text-xs text-gray-500">
                                {formatDate(entry.created_at)}
                              </span>
                            </div>
                            <h4 className="font-medium text-sm mb-1">{entry.title}</h4>
                            <p className="text-xs text-gray-600">
                              {entry.content.substring(0, 150)}...
                            </p>
                          </div>
                        ))}
                      </div>
                    )}
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Active Destinations</CardTitle>
                    <CardDescription>
                      Client's current goals and aspirations
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    {destinations.length === 0 ? (
                      <p className="text-gray-500 text-sm">No destinations set</p>
                    ) : (
                      <div className="space-y-3">
                        {destinations.map((destination) => (
                          <div key={destination.id} className="p-3 border rounded-lg">
                            <div className="flex items-center justify-between mb-2">
                              <Badge variant="outline">{destination.status}</Badge>
                              <span className="text-xs text-gray-500">
                                {formatDate(destination.created_at)}
                              </span>
                            </div>
                            <h4 className="font-medium text-sm mb-1">{destination.title}</h4>
                            <p className="text-xs text-gray-600">
                              {destination.description.substring(0, 100)}...
                            </p>
                          </div>
                        ))}
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>
            </TabsContent>
          </div>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
}