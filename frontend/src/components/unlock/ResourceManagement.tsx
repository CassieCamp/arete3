'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { BookOpen, Plus, Edit, Trash2, ExternalLink, FileText, Video, Link, Settings, X } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';

interface CoachResource {
  id: string;
  title: string;
  description: string;
  resource_url: string;
  resource_type: string;
  is_template: boolean;
  client_specific: boolean;
  target_client_id: string | null;
  category: string;
  tags: string[];
  created_at: string;
}

interface ResourceManagementProps {
  resources: CoachResource[];
  onUpdate: () => void;
}

interface ResourceFormData {
  title: string;
  description: string;
  resource_url: string;
  resource_type: string;
  category: string;
  tags: string;
}

export function ResourceManagement({ resources, onUpdate }: ResourceManagementProps) {
  const { getAuthToken } = useAuth();
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingResource, setEditingResource] = useState<CoachResource | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState<ResourceFormData>({
    title: '',
    description: '',
    resource_url: '',
    resource_type: 'article',
    category: 'reading',
    tags: ''
  });

  const resourceTypes = [
    { value: 'document', label: 'Document', icon: FileText },
    { value: 'article', label: 'Article', icon: BookOpen },
    { value: 'video', label: 'Video', icon: Video },
    { value: 'tool', label: 'Tool', icon: Settings }
  ];

  const categories = [
    { value: 'exercise', label: 'Exercise' },
    { value: 'assessment', label: 'Assessment' },
    { value: 'reading', label: 'Reading' },
    { value: 'framework', label: 'Framework' }
  ];

  const getResourceIcon = (type: string) => {
    const resourceType = resourceTypes.find(rt => rt.value === type);
    return resourceType ? resourceType.icon : BookOpen;
  };

  const getResourceTypeColor = (type: string) => {
    switch (type) {
      case 'document':
        return 'bg-blue-100 text-blue-800';
      case 'article':
        return 'bg-green-100 text-green-800';
      case 'video':
        return 'bg-purple-100 text-purple-800';
      case 'tool':
        return 'bg-orange-100 text-orange-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'exercise':
        return 'bg-red-100 text-red-800';
      case 'assessment':
        return 'bg-yellow-100 text-yellow-800';
      case 'reading':
        return 'bg-indigo-100 text-indigo-800';
      case 'framework':
        return 'bg-pink-100 text-pink-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const resetForm = () => {
    setFormData({
      title: '',
      description: '',
      resource_url: '',
      resource_type: 'article',
      category: 'reading',
      tags: ''
    });
    setError(null);
  };

  const handleCreate = () => {
    resetForm();
    setEditingResource(null);
    setShowCreateModal(true);
  };

  const handleEdit = (resource: CoachResource) => {
    setFormData({
      title: resource.title,
      description: resource.description,
      resource_url: resource.resource_url,
      resource_type: resource.resource_type,
      category: resource.category,
      tags: resource.tags.join(', ')
    });
    setEditingResource(resource);
    setShowCreateModal(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.title.trim() || !formData.resource_url.trim()) {
      setError('Title and URL are required');
      return;
    }

    try {
      setIsSubmitting(true);
      setError(null);

      const token = await getAuthToken();
      if (!token) throw new Error('No authentication token');

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const url = editingResource 
        ? `${apiUrl}/api/v1/unlock/resources/${editingResource.id}`
        : `${apiUrl}/api/v1/unlock/resources`;
      
      const method = editingResource ? 'PUT' : 'POST';
      
      const payload = {
        title: formData.title.trim(),
        description: formData.description.trim(),
        resource_url: formData.resource_url.trim(),
        resource_type: formData.resource_type,
        category: formData.category,
        tags: formData.tags.split(',').map(tag => tag.trim()).filter(tag => tag.length > 0),
        is_template: false,
        client_specific: false
      };

      const response = await fetch(url, {
        method,
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to save resource');
      }

      resetForm();
      setShowCreateModal(false);
      setEditingResource(null);
      onUpdate();
    } catch (error) {
      console.error('Error saving resource:', error);
      setError(error instanceof Error ? error.message : 'Failed to save resource');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async (resourceId: string) => {
    if (!confirm('Are you sure you want to delete this resource?')) {
      return;
    }

    try {
      const token = await getAuthToken();
      if (!token) throw new Error('No authentication token');

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/v1/unlock/resources/${resourceId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to delete resource');
      }

      onUpdate();
    } catch (error) {
      console.error('Error deleting resource:', error);
    }
  };

  const handleClose = () => {
    if (!isSubmitting) {
      setShowCreateModal(false);
      setEditingResource(null);
      resetForm();
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-lg font-semibold text-gray-800">Resource Library</h2>
          <p className="text-gray-600">Manage your coaching resources and materials</p>
        </div>
        <Button
          onClick={handleCreate}
          className="bg-blue-600 text-white hover:bg-blue-700"
        >
          <Plus className="w-4 h-4 mr-2" />
          Add Resource
        </Button>
      </div>

      {/* Resources Grid */}
      {resources.length === 0 ? (
        <Card>
          <CardContent className="text-center py-8">
            <BookOpen className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-600 mb-2">No resources yet</h3>
            <p className="text-gray-500 mb-4">Create your first coaching resource to get started.</p>
            <Button
              onClick={handleCreate}
              className="bg-blue-600 text-white hover:bg-blue-700"
            >
              Add Resource
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {resources.map((resource) => {
            const IconComponent = getResourceIcon(resource.resource_type);
            return (
              <Card key={resource.id} className="hover:shadow-md transition-shadow">
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-2">
                      <div className="p-2 bg-gray-100 rounded-lg">
                        <IconComponent className="w-4 h-4 text-gray-600" />
                      </div>
                      <div className="flex flex-col gap-1">
                        <Badge className={getResourceTypeColor(resource.resource_type)}>
                          {resource.resource_type}
                        </Badge>
                        <Badge variant="outline" className={getCategoryColor(resource.category)}>
                          {resource.category}
                        </Badge>
                      </div>
                    </div>
                    <div className="flex gap-1">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleEdit(resource)}
                        className="h-8 w-8 p-0"
                      >
                        <Edit className="w-3 h-3" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDelete(resource.id)}
                        className="h-8 w-8 p-0 text-red-600 hover:text-red-700"
                      >
                        <Trash2 className="w-3 h-3" />
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <h3 className="font-semibold text-gray-900 mb-2">{resource.title}</h3>
                  <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                    {resource.description}
                  </p>
                  
                  {resource.tags.length > 0 && (
                    <div className="flex flex-wrap gap-1 mb-3">
                      {resource.tags.slice(0, 3).map((tag, index) => (
                        <Badge key={index} variant="secondary" className="text-xs">
                          {tag}
                        </Badge>
                      ))}
                      {resource.tags.length > 3 && (
                        <Badge variant="secondary" className="text-xs">
                          +{resource.tags.length - 3}
                        </Badge>
                      )}
                    </div>
                  )}
                  
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => window.open(resource.resource_url, '_blank')}
                    className="w-full"
                  >
                    <ExternalLink className="w-3 h-3 mr-2" />
                    Open Resource
                  </Button>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}

      {/* Create/Edit Modal */}
      <Dialog open={showCreateModal} onOpenChange={handleClose}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <div className="flex items-center justify-between">
              <DialogTitle>
                {editingResource ? 'Edit Resource' : 'Add New Resource'}
              </DialogTitle>
              <Button
                variant="ghost"
                size="sm"
                onClick={handleClose}
                disabled={isSubmitting}
                className="h-8 w-8 p-0"
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          </DialogHeader>

          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-sm text-red-600">{error}</p>
              </div>
            )}

            <div className="space-y-2">
              <Label htmlFor="title">Title *</Label>
              <Input
                id="title"
                value={formData.title}
                onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
                placeholder="Resource title"
                disabled={isSubmitting}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                value={formData.description}
                onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                placeholder="Brief description of the resource"
                disabled={isSubmitting}
                className="min-h-[80px]"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="resource_url">URL *</Label>
              <Input
                id="resource_url"
                type="url"
                value={formData.resource_url}
                onChange={(e) => setFormData(prev => ({ ...prev, resource_url: e.target.value }))}
                placeholder="https://example.com/resource"
                disabled={isSubmitting}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="resource_type">Type</Label>
                <Select
                  value={formData.resource_type}
                  onValueChange={(value) => setFormData(prev => ({ ...prev, resource_type: value }))}
                  disabled={isSubmitting}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {resourceTypes.map((type) => (
                      <SelectItem key={type.value} value={type.value}>
                        {type.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="category">Category</Label>
                <Select
                  value={formData.category}
                  onValueChange={(value) => setFormData(prev => ({ ...prev, category: value }))}
                  disabled={isSubmitting}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {categories.map((category) => (
                      <SelectItem key={category.value} value={category.value}>
                        {category.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="tags">Tags (comma-separated)</Label>
              <Input
                id="tags"
                value={formData.tags}
                onChange={(e) => setFormData(prev => ({ ...prev, tags: e.target.value }))}
                placeholder="leadership, communication, assessment"
                disabled={isSubmitting}
              />
            </div>

            <div className="flex gap-3 pt-2">
              <Button
                type="button"
                variant="outline"
                onClick={handleClose}
                disabled={isSubmitting}
                className="flex-1"
              >
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={isSubmitting || !formData.title.trim() || !formData.resource_url.trim()}
                className="flex-1 bg-blue-600 text-white hover:bg-blue-700"
              >
                {isSubmitting ? 'Saving...' : (editingResource ? 'Update' : 'Create')}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}