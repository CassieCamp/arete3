"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";

interface UploadFormData {
  file: File | null;
  category: string;
  description: string;
}

const DOCUMENT_CATEGORIES = [
  { value: "resume", label: "Resume" },
  { value: "performance_review", label: "Performance Review" },
  { value: "goals_objectives", label: "Goals & Objectives" },
  { value: "feedback", label: "Feedback" },
  { value: "assessment", label: "Assessment" },
  { value: "development_plan", label: "Development Plan" },
  { value: "project_documentation", label: "Project Documentation" },
  { value: "meeting_notes", label: "Meeting Notes" },
  { value: "other", label: "Other" },
];

const SUPPORTED_FILE_TYPES = [
  "pdf", "docx", "doc", "txt", "rtf", "odt"
];

export default function DocumentUploadPage() {
  const router = useRouter();
  const { getAuthToken } = useAuth();
  const [formData, setFormData] = useState<UploadFormData>({
    file: null,
    category: "",
    description: "",
  });
  const [isUploading, setIsUploading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] || null;
    
    if (file) {
      // Validate file type
      const fileExtension = file.name.split('.').pop()?.toLowerCase();
      if (!fileExtension || !SUPPORTED_FILE_TYPES.includes(fileExtension)) {
        setMessage({
          type: 'error',
          text: `Unsupported file type. Supported types: ${SUPPORTED_FILE_TYPES.join(', ')}`
        });
        e.target.value = ''; // Clear the input
        return;
      }
      
      // Validate file size (10MB limit)
      const maxSize = 10 * 1024 * 1024; // 10MB in bytes
      if (file.size > maxSize) {
        setMessage({
          type: 'error',
          text: 'File size must be less than 10MB'
        });
        e.target.value = ''; // Clear the input
        return;
      }
      
      setMessage(null); // Clear any previous error messages
    }
    
    setFormData(prev => ({
      ...prev,
      file
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.file || !formData.category) {
      setMessage({
        type: 'error',
        text: 'Please select a file and category'
      });
      return;
    }

    setIsUploading(true);
    setMessage(null);

    try {
      // Get authentication token
      const token = await getAuthToken();
      if (!token) {
        throw new Error('Authentication token not available');
      }

      // Create FormData object
      const uploadFormData = new FormData();
      uploadFormData.append('file', formData.file);
      uploadFormData.append('category', formData.category);
      if (formData.description.trim()) {
        uploadFormData.append('description', formData.description.trim());
      }

      // Make API request
      const response = await fetch('http://localhost:8000/api/v1/documents/upload', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: uploadFormData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Upload failed with status ${response.status}`);
      }

      const result = await response.json();
      
      setMessage({
        type: 'success',
        text: `Document "${result.file_name}" uploaded successfully!`
      });

      // Reset form
      setFormData({
        file: null,
        category: "",
        description: "",
      });

      // Clear file input
      const fileInput = document.getElementById('file') as HTMLInputElement;
      if (fileInput) {
        fileInput.value = '';
      }

    } catch (error) {
      console.error('Upload error:', error);
      setMessage({
        type: 'error',
        text: error instanceof Error ? error.message : 'Failed to upload document'
      });
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-2xl mx-auto">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-extrabold text-gray-900">
            Upload Document
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Upload your documents for AI-enhanced coaching insights
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Document Upload</CardTitle>
            <CardDescription>
              Upload documents such as resumes, performance reviews, or development plans
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* File Input */}
              <div className="space-y-2">
                <Label htmlFor="file">Document File *</Label>
                <Input
                  id="file"
                  type="file"
                  accept=".pdf,.docx,.doc,.txt,.rtf,.odt"
                  onChange={handleFileChange}
                  required
                />
                <p className="text-sm text-gray-500">
                  Supported formats: PDF, DOCX, DOC, TXT, RTF, ODT (max 10MB)
                </p>
              </div>

              {/* Category Dropdown */}
              <div className="space-y-2">
                <Label htmlFor="category">Category *</Label>
                <select
                  id="category"
                  value={formData.category}
                  onChange={(e) => setFormData(prev => ({
                    ...prev,
                    category: e.target.value
                  }))}
                  className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-base shadow-xs transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50 md:text-sm"
                  required
                >
                  <option value="">Select a category</option>
                  {DOCUMENT_CATEGORIES.map((category) => (
                    <option key={category.value} value={category.value}>
                      {category.label}
                    </option>
                  ))}
                </select>
              </div>

              {/* Description Textarea */}
              <div className="space-y-2">
                <Label htmlFor="description">Description (Optional)</Label>
                <Textarea
                  id="description"
                  placeholder="Add a description or notes about this document..."
                  value={formData.description}
                  onChange={(e) => setFormData(prev => ({
                    ...prev,
                    description: e.target.value
                  }))}
                  rows={3}
                />
              </div>

              {/* Message Display */}
              {message && (
                <div className={`p-4 rounded-md ${
                  message.type === 'success' 
                    ? 'bg-green-50 text-green-800 border border-green-200' 
                    : 'bg-red-50 text-red-800 border border-red-200'
                }`}>
                  {message.text}
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex gap-4">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => router.back()}
                  className="flex-1"
                  disabled={isUploading}
                >
                  Back
                </Button>
                <Button 
                  type="submit" 
                  className="flex-1"
                  disabled={isUploading || !formData.file || !formData.category}
                >
                  {isUploading ? 'Uploading...' : 'Upload Document'}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}