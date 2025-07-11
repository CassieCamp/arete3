"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
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

interface DocumentListProps {
  limit?: number;
  showUploadButton?: boolean;
  onUploadClick?: () => void;
  compact?: boolean;
}

export function DocumentList({ 
  limit, 
  showUploadButton = true, 
  onUploadClick,
  compact = false 
}: DocumentListProps) {
  const { getAuthToken, isAuthenticated, user } = useAuth();
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDocuments = async () => {
    try {
      setIsLoading(true);
      setError(null);

      const token = await getAuthToken();
      if (!token) {
        throw new Error('Authentication token not available');
      }

      const url = limit 
        ? `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/documents/?limit=${limit}`
        : `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/documents/`;

      const response = await fetch(url, {
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
  }, [isAuthenticated, user, limit]);

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
      ...(compact ? {} : { hour: '2-digit', minute: '2-digit' })
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
      <div className="text-center py-4">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
        <p className="mt-2 text-gray-600 text-sm">Loading documents...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 bg-red-50 text-red-800 border border-red-200 rounded-md">
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
    );
  }

  if (documents.length === 0) {
    return (
      <Card>
        <CardContent className="text-center py-8">
          <div className="text-4xl mb-4">📁</div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            No documents yet
          </h3>
          <p className="text-gray-600 mb-4 text-sm">
            Upload your first document to get started with AI-enhanced coaching insights.
          </p>
          {showUploadButton && (
            <Button
              onClick={onUploadClick}
              className="bg-primary hover:bg-primary/90"
              size="sm"
            >
              Upload Your First Document
            </Button>
          )}
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {showUploadButton && (
        <div className="flex justify-between items-center">
          <p className="text-sm text-gray-600">
            {documents.length} document{documents.length !== 1 ? 's' : ''}
            {limit && documents.length >= limit ? ` (showing ${limit})` : ''}
          </p>
          <Button
            onClick={onUploadClick}
            size="sm"
            className="bg-primary hover:bg-primary/90"
          >
            Upload New
          </Button>
        </div>
      )}

      <div className={compact ? "space-y-3" : "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"}>
        {documents.map((document) => (
          <Card key={document.id} className={`hover:shadow-md transition-shadow ${compact ? 'p-3' : ''}`}>
            <CardHeader className={compact ? "pb-2" : "pb-3"}>
              <div className="flex items-start justify-between">
                <div className="flex items-center space-x-2 min-w-0 flex-1">
                  <span className={compact ? "text-lg" : "text-2xl"}>{getFileTypeIcon(document.file_type)}</span>
                  <div className="min-w-0 flex-1">
                    <CardTitle className={`font-medium text-gray-900 truncate ${compact ? 'text-sm' : 'text-sm'}`}>
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
            {!compact && (
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
            )}
            {compact && (
              <CardContent className="pt-0">
                <div className="text-xs text-gray-500">
                  {formatDate(document.created_at)} • {formatFileSize(document.file_size)}
                </div>
              </CardContent>
            )}
          </Card>
        ))}
      </div>
    </div>
  );
}