"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useAuth } from "@/context/AuthContext";
import { sessionInsightService } from "@/services/sessionInsightService";

interface CoachingRelationship {
  id: string;
  coach_user_id: string;
  client_user_id: string;
  status: "pending" | "active" | "declined";
  created_at: string;
  updated_at: string;
  coach_email?: string;
  client_email?: string;
}

interface InsightSubmissionComponentProps {
  relationship: CoachingRelationship;
  onInsightCreated: () => void;
  onBack: () => void;
  getOtherUserName: (relationship: CoachingRelationship) => string;
}

export function InsightSubmissionComponent({
  relationship,
  onInsightCreated,
  onBack,
  getOtherUserName
}: InsightSubmissionComponentProps) {
  const { getAuthToken } = useAuth();
  
  // Form state
  const [sessionTitle, setSessionTitle] = useState("");
  const [sessionDate, setSessionDate] = useState("");
  const [inputMethod, setInputMethod] = useState<'file' | 'text'>('file');
  const [transcriptText, setTranscriptText] = useState("");
  const [transcriptFile, setTranscriptFile] = useState<File | null>(null);
  
  // UI state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState(false);

  const handleFileSelect = (file: File) => {
    // Validate file type
    const allowedTypes = ['text/plain', 'application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    if (!allowedTypes.includes(file.type)) {
      setError('Please upload a text file (.txt), PDF (.pdf), or Word document (.docx)');
      return;
    }

    // Validate file size (10MB limit)
    const maxSize = 10 * 1024 * 1024; // 10MB
    if (file.size > maxSize) {
      setError('File size must be less than 10MB');
      return;
    }

    setTranscriptFile(file);
    setError(null);
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFileSelect(e.target.files[0]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Validation
    if (inputMethod === 'file' && !transcriptFile) {
      setError('Please select a transcript file');
      return;
    }

    if (inputMethod === 'text' && !transcriptText.trim()) {
      setError('Please enter transcript text');
      return;
    }

    if (inputMethod === 'text' && transcriptText.trim().length < 50) {
      setError('Transcript text must be at least 50 characters long');
      return;
    }

    try {
      setLoading(true);
      const token = await getAuthToken();
      if (!token) {
        throw new Error('Authentication token not available');
      }

      if (inputMethod === 'file' && transcriptFile) {
        await sessionInsightService.createSessionInsightFromFile(token, {
          coaching_relationship_id: relationship.id,
          transcript_file: transcriptFile,
        });
      } else if (inputMethod === 'text') {
        await sessionInsightService.createSessionInsightFromText(token, {
          coaching_relationship_id: relationship.id,
          transcript_text: transcriptText,
        });
      }

      // Success - notify parent component
      onInsightCreated();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create session insight');
    } finally {
      setLoading(false);
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-2xl font-bold text-gray-900">Create Session Insight</h3>
          <p className="text-sm text-gray-600">
            For coaching relationship with {getOtherUserName(relationship)}
          </p>
        </div>
        <Button variant="outline" onClick={onBack}>
          ← Back to Timeline
        </Button>
      </div>

      {/* Error Message */}
      {error && (
        <div className="p-4 bg-red-50 text-red-800 border border-red-200 rounded-md">
          <p className="font-medium">Error</p>
          <p className="text-sm">{error}</p>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Input Method Selection */}
        <Card>
          <CardHeader>
            <CardTitle>Transcript Input</CardTitle>
            <CardDescription>
              Choose how you'd like to provide the session transcript
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Method Toggle */}
            <div className="flex bg-gray-100 rounded-lg p-1">
              <button
                type="button"
                onClick={() => setInputMethod('file')}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  inputMethod === 'file'
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Upload File
              </button>
              <button
                type="button"
                onClick={() => setInputMethod('text')}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  inputMethod === 'text'
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Paste Text
              </button>
            </div>

            {/* File Upload */}
            {inputMethod === 'file' && (
              <div className="space-y-4">
                <div
                  className={`relative border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
                    dragActive
                      ? 'border-blue-400 bg-blue-50'
                      : 'border-gray-300 hover:border-gray-400'
                  }`}
                  onDragEnter={handleDrag}
                  onDragLeave={handleDrag}
                  onDragOver={handleDrag}
                  onDrop={handleDrop}
                >
                  {transcriptFile ? (
                    <div className="space-y-2">
                      <div className="text-2xl">📄</div>
                      <p className="font-medium text-gray-900">{transcriptFile.name}</p>
                      <p className="text-sm text-gray-600">
                        {formatFileSize(transcriptFile.size)}
                      </p>
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        onClick={() => setTranscriptFile(null)}
                      >
                        Remove File
                      </Button>
                    </div>
                  ) : (
                    <div className="space-y-2">
                      <div className="text-4xl text-gray-400">📁</div>
                      <p className="text-lg font-medium text-gray-900">
                        Drop your transcript file here
                      </p>
                      <p className="text-sm text-gray-600">
                        or click to browse files
                      </p>
                      <p className="text-xs text-gray-500">
                        Supports .txt, .pdf, and .docx files up to 10MB
                      </p>
                    </div>
                  )}
                  <input
                    type="file"
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                    accept=".txt,.pdf,.docx"
                    onChange={handleFileInputChange}
                    disabled={loading}
                  />
                </div>
              </div>
            )}

            {/* Text Input */}
            {inputMethod === 'text' && (
              <div className="space-y-2">
                <Label htmlFor="transcriptText">Transcript Text</Label>
                <Textarea
                  id="transcriptText"
                  value={transcriptText}
                  onChange={(e) => setTranscriptText(e.target.value)}
                  placeholder="Paste your session transcript here..."
                  className="min-h-[200px]"
                  disabled={loading}
                />
                <p className="text-xs text-gray-500">
                  Minimum 50 characters required. Current: {transcriptText.length} characters
                </p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Submit Button */}
        <div className="flex justify-end space-x-4">
          <Button type="button" variant="outline" onClick={onBack} disabled={loading}>
            Cancel
          </Button>
          <Button type="submit" disabled={loading} className="bg-blue-600 hover:bg-blue-700">
            {loading ? (
              <div className="flex items-center space-x-2">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                <span>Processing...</span>
              </div>
            ) : (
              'Create Session Insight'
            )}
          </Button>
        </div>
      </form>
    </div>
  );
}