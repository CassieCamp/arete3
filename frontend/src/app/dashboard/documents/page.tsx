"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";

interface Document {
  id: string;
  user_id: string;
  clerk_user_id: string;
  file_name: string;
  file_type: string;
  file_size: number;
  s3_url?: string;
  local_path?: string;
  extracted_text?: string;
  category: string;
  tags: string[];
  description?: string;
  is_processed: boolean;
  processing_error?: string;
  created_at: string;
  updated_at: string;
}

const DOCUMENT_CATEGORIES = {
  resume: "Resume",
  performance_review: "Performance Review",
  goals_objectives: "Goals & Objectives",
  feedback: "Feedback",
  assessment: "Assessment",
  development_plan: "Development Plan",
  project_documentation: "Project Documentation",
  meeting_notes: "Meeting Notes",
  other: "Other",
};

export default function DocumentLibraryPage() {
  const router = useRouter();
  const { getAuthToken, isAuthenticated, user } = useAuth();
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDocuments = async () => {
    try {
      setIsLoading(true);
      setError(null);

      // Get authentication token
      const token = await getAuthToken();
      if (!token) {
        throw new Error('Authentication token not available');
      }

      // Make API request to fetch documents
      const response = await fetch('http://localhost:8000/api/v1/documents/', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Failed to fetch documents with status ${response.status}`);
      }

      const documentsData = await response.json();
      setDocuments(documentsData);

    } catch (error) {
      console.error('Error fetching documents:', error);
      setError(error instanceof Error ? error.message : 'Failed to fetch documents');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (isAuthenticated && user) {
      fetchDocuments();
    }
  }, [isAuthenticated, user]);

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getCategoryLabel = (category: string): string => {
    return DOCUMENT_CATEGORIES[category as keyof typeof DOCUMENT_CATEGORIES] || category;
  };

  const getFileTypeIcon = (fileType: string): string => {
    switch (fileType.toLowerCase()) {
      case 'pdf':
        return '📄';
      case 'docx':
      case 'doc':
        return '📝';
      case 'txt':
        return '📃';
      default:
        return '📄';
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-6xl mx-auto">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading your documents...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h2 className="text-3xl font-extrabold text-gray-900">
            Document Library
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Manage and view your uploaded documents
          </p>
        </div>

        {/* Action Bar */}
        <div className="mb-6 flex justify-between items-center">
          <div className="flex items-center space-x-4">
            <p className="text-sm text-gray-600">
              {documents.length} document{documents.length !== 1 ? 's' : ''} total
            </p>
          </div>
          <Button 
            onClick={() => router.push('/dashboard/documents/upload')}
            className="bg-blue-600 hover:bg-blue-700"
          >
            Upload New Document
          </Button>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 text-red-800 border border-red-200 rounded-md">
            <p className="font-medium">Error loading documents</p>
            <p className="text-sm">{error}</p>
            <Button 
              onClick={fetchDocuments}
              variant="outline"
              size="sm"
              className="mt-2"
            >
              Try Again
            </Button>
          </div>
        )}

        {/* Documents Grid */}
        {documents.length === 0 && !error ? (
          <Card>
            <CardContent className="text-center py-12">
              <div className="text-6xl mb-4">📁</div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                No documents yet
              </h3>
              <p className="text-gray-600 mb-6">
                Upload your first document to get started with AI-enhanced coaching insights.
              </p>
              <Button 
                onClick={() => router.push('/dashboard/documents/upload')}
                className="bg-blue-600 hover:bg-blue-700"
              >
                Upload Your First Document
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {documents.map((document) => (
              <Card key={document.id} className="hover:shadow-lg transition-shadow">
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center space-x-2">
                      <span className="text-2xl">{getFileTypeIcon(document.file_type)}</span>
                      <div className="min-w-0 flex-1">
                        <CardTitle className="text-sm font-medium text-gray-900 truncate">
                          {document.file_name}
                        </CardTitle>
                        <CardDescription className="text-xs">
                          {getCategoryLabel(document.category)}
                        </CardDescription>
                      </div>
                    </div>
                    <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                      document.is_processed 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {document.is_processed ? 'Processed' : 'Processing'}
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="pt-0">
                  <div className="space-y-2 text-sm text-gray-600">
                    <div className="flex justify-between">
                      <span>Size:</span>
                      <span>{formatFileSize(document.file_size)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Type:</span>
                      <span className="uppercase">{document.file_type}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Uploaded:</span>
                      <span>{formatDate(document.created_at)}</span>
                    </div>
                    {document.description && (
                      <div className="pt-2 border-t">
                        <p className="text-xs text-gray-500 line-clamp-2">
                          {document.description}
                        </p>
                      </div>
                    )}
                    {document.processing_error && (
                      <div className="pt-2 border-t">
                        <p className="text-xs text-red-600">
                          Processing error: {document.processing_error}
                        </p>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}