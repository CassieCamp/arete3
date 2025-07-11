'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Users, Clock, FileText, Plus, Eye, MessageSquare, Mail, Calendar } from 'lucide-react';
import { ClientDetailsModal } from './ClientDetailsModal';
import { InviteClientModal } from './InviteClientModal';
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

interface ClientManagementProps {
  clients: CoachClient[];
  onUpdate: () => void;
}

export function ClientManagement({ clients, onUpdate }: ClientManagementProps) {
  const { getAuthToken } = useAuth();
  const [selectedClient, setSelectedClient] = useState<CoachClient | null>(null);
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const activeClients = clients.filter(c => c.relationship_status === 'active');
  const pendingClients = clients.filter(c => c.relationship_status === 'pending' || c.relationship_status === 'pending_by_coach');

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'Never';
    return new Date(dateString).toLocaleDateString();
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'pending':
      case 'pending_by_coach':
        return 'bg-orange-100 text-orange-800';
      case 'declined':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'active':
        return 'Active';
      case 'pending':
      case 'pending_by_coach':
        return 'Pending';
      case 'declined':
        return 'Declined';
      default:
        return status;
    }
  };

  const handleResendInvite = async (clientId: string) => {
    try {
      setIsLoading(true);
      const token = await getAuthToken();
      if (!token) throw new Error('No authentication token');

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/v1/unlock/clients/${clientId}/resend-invite`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to resend invitation');
      }

      onUpdate();
    } catch (error) {
      console.error('Error resending invite:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Users className="w-6 h-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Active Clients</p>
                <p className="text-2xl font-semibold text-gray-900">{activeClients.length}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="p-2 bg-orange-100 rounded-lg">
                <Clock className="w-6 h-6 text-orange-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Pending Invites</p>
                <p className="text-2xl font-semibold text-gray-900">{pendingClients.length}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-lg">
                <FileText className="w-6 h-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Entries</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {activeClients.reduce((sum, client) => sum + client.entries_count, 0)}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Action Buttons */}
      <div className="flex justify-between items-center">
        <h2 className="text-lg font-semibold text-gray-800">Client List</h2>
        <Button
          onClick={() => setShowInviteModal(true)}
          className="bg-blue-600 text-white hover:bg-blue-700"
        >
          <Plus className="w-4 h-4 mr-2" />
          Invite Client
        </Button>
      </div>

      {/* Pending Invitations */}
      {pendingClients.length > 0 && (
        <Card className="border-orange-200 bg-orange-50">
          <CardHeader>
            <CardTitle className="text-orange-800 flex items-center">
              <Clock className="w-5 h-5 mr-2" />
              Pending Invitations
            </CardTitle>
            <CardDescription>
              These clients have been invited but haven't accepted yet.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {pendingClients.map((client) => (
                <div key={client.id} className="flex items-center justify-between bg-white rounded-lg p-4 border">
                  <div className="flex items-center space-x-3">
                    <div className="p-2 bg-orange-100 rounded-full">
                      <Mail className="w-4 h-4 text-orange-600" />
                    </div>
                    <div>
                      <div className="font-medium text-gray-900">{client.email}</div>
                      <div className="text-sm text-gray-600 flex items-center">
                        <Calendar className="w-3 h-3 mr-1" />
                        Invited {formatDate(client.created_at)}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Badge className={getStatusColor(client.relationship_status)}>
                      {getStatusText(client.relationship_status)}
                    </Badge>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleResendInvite(client.id)}
                      disabled={isLoading}
                    >
                      Resend
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Active Clients */}
      <Card>
        <CardHeader>
          <CardTitle>Active Clients</CardTitle>
          <CardDescription>
            Clients who have accepted your coaching invitation.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {activeClients.length === 0 ? (
            <div className="text-center py-8">
              <Users className="w-12 h-12 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-600 mb-2">No active clients yet</h3>
              <p className="text-gray-500 mb-4">Invite your first client to get started.</p>
              <Button
                onClick={() => setShowInviteModal(true)}
                className="bg-blue-600 text-white hover:bg-blue-700"
              >
                Invite Client
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              {activeClients.map((client) => (
                <div
                  key={client.id}
                  className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
                  onClick={() => setSelectedClient(client)}
                >
                  <div className="flex items-center space-x-4">
                    <div className="p-2 bg-blue-100 rounded-full">
                      <Users className="w-5 h-5 text-blue-600" />
                    </div>
                    <div>
                      <div className="font-medium text-gray-900">{client.name}</div>
                      <div className="text-sm text-gray-600">{client.email}</div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    <div className="text-right">
                      <div className="text-sm font-medium text-gray-900">
                        {client.entries_count} entries
                      </div>
                      <div className="text-xs text-gray-600">
                        Last: {formatDate(client.last_entry_date)}
                      </div>
                    </div>
                    <Badge className={getStatusColor(client.relationship_status)}>
                      {getStatusText(client.relationship_status)}
                    </Badge>
                    <Button variant="outline" size="sm">
                      <Eye className="w-4 h-4 mr-1" />
                      View
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Client Details Modal */}
      {selectedClient && (
        <ClientDetailsModal
          client={selectedClient}
          isOpen={!!selectedClient}
          onClose={() => setSelectedClient(null)}
          onUpdate={onUpdate}
        />
      )}

      {/* Invite Client Modal */}
      <InviteClientModal
        isOpen={showInviteModal}
        onClose={() => setShowInviteModal(false)}
        onSuccess={onUpdate}
      />
    </div>
  );
}