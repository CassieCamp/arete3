'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  FileText, 
  Upload, 
  Loader2, 
  AlertCircle,
  Type,
  File
} from 'lucide-react';
import { sessionInsightService, CreateUnpairedTranscriptInsightRequest } from '@/services/sessionInsightService';
import { useAuth } from '@/context/AuthContext';
import { useToast } from '@/hooks/use-toast';

interface UnpairedInsightUploadProps {
  onSuccess?: () => void;
  onCancel?: () => void;
}

const SUPPORTED_FILE_TYPES = [
  "pdf", "docx", "doc", "txt", "rtf", "odt"
];

export function UnpairedInsightUpload({ onSuccess, onCancel }: UnpairedInsightUploadProps) {
  const { getAuthToken } = useAuth();
  const { toast } = useToast();
  
  const [activeTab, setActiveTab] = useState<'text' | 'file'>('text');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Text input form data
  const [transcriptText, setTranscriptText] = useState('');
  
  // File upload form data
  const [transcriptFile, setTranscriptFile] = useState<File | null>(null);

  const handleTextInputChange = (value: string) => {
    setTranscriptText(value);
    // Clear error when user starts typing
    if (error) setError(null);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] || null;
    
    if (file) {
      // Validate file type
      const fileExtension = file.name.split('.').pop()?.toLowerCase();
      if (!fileExtension || !SUPPORTED_FILE_TYPES.includes(fileExtension)) {
        setError(`Unsupported file type. Supported types: ${SUPPORTED_FILE_TYPES.join(', ')}`);
        e.target.value = ''; // Clear the input
        return;
      }
      
      // Validate file size (10MB limit)
      const maxSize = 10 * 1024 * 1024; // 10MB in bytes
      if (file.size > maxSize) {
        setError('File size must be less than 10MB');
        e.target.value = ''; // Clear the input
        return;
      }
      
      setError(null); // Clear any previous error messages
    }
    
    setTranscriptFile(file);
  };

  const validateTextForm = () => {
    if (!transcriptText.trim()) {
      setError('Transcript content is required');
      return false;
    }
    return true;
  };

  const validateFileForm = () => {
    if (!transcriptFile) {
      setError('Please select a transcript file');
      return false;
    }
    return true;
  };

  const handleTextSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateTextForm()) return;

    try {
      setLoading(true);
      setError(null);
      
      const token = await getAuthToken();
      if (!token) {
        throw new Error("Authentication token not available");
      }

      const requestData: CreateUnpairedTranscriptInsightRequest = {
        transcript_text: transcriptText.trim(),
      };

      await sessionInsightService.createUnpairedInsightFromTranscript(token, requestData);
      
      toast({
        title: "Success!",
        description: "Your transcript is being processed. You'll receive comprehensive insights shortly.",
      });

      // Reset form
      setTranscriptText('');

      onSuccess?.();
    } catch (err) {
      console.error('Error creating insight from transcript:', err);
      const errorMessage = err instanceof Error ? err.message : 'Failed to process transcript. Please try again.';
      setError(errorMessage);
      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleFileSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateFileForm()) return;

    try {
      setLoading(true);
      setError(null);
      
      const token = await getAuthToken();
      if (!token) {
        throw new Error("Authentication token not available");
      }

      const requestData = {
        transcript_file: transcriptFile!,
      };

      await sessionInsightService.createUnpairedInsightFromFile(token, requestData);
      
      toast({
        title: "Success!",
        description: "Your transcript file is being processed. You'll receive comprehensive insights shortly.",
      });

      // Reset form
      setTranscriptFile(null);

      // Clear file input
      const fileInput = document.getElementById('transcript_file') as HTMLInputElement;
      if (fileInput) {
        fileInput.value = '';
      }

      onSuccess?.();
    } catch (err) {
      console.error('Error creating insight from file:', err);
      const errorMessage = err instanceof Error ? err.message : 'Failed to process transcript file. Please try again.';
      setError(errorMessage);
      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <Card>
        <CardHeader>
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <FileText className="h-6 w-6 text-blue-600" />
            </div>
            <div>
              <CardTitle>Create Session Insight</CardTitle>
              <CardDescription>
                Upload a transcript or paste session content to generate comprehensive coaching insights
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        
        <CardContent>
          <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as 'text' | 'file')}>
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="text" className="flex items-center gap-2">
                <Type className="h-4 w-4" />
                Paste Text
              </TabsTrigger>
              <TabsTrigger value="file" className="flex items-center gap-2">
                <File className="h-4 w-4" />
                Upload File
              </TabsTrigger>
            </TabsList>

            <TabsContent value="text" className="mt-6">
              <form onSubmit={handleTextSubmit} className="space-y-6">
                {error && (
                  <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-md text-red-700">
                    <AlertCircle className="h-4 w-4" />
                    <span className="text-sm">{error}</span>
                  </div>
                )}

                <div className="space-y-2">
                  <Label htmlFor="transcript_text">Transcript Content</Label>
                  <Textarea
                    id="transcript_text"
                    placeholder="Paste your session transcript here..."
                    value={transcriptText}
                    onChange={(e) => handleTextInputChange(e.target.value)}
                    disabled={loading}
                    rows={12}
                    className="w-full resize-none"
                  />
                  <p className="text-xs text-gray-500">
                    Paste the full transcript of your coaching session for comprehensive AI analysis
                  </p>
                </div>

                <div className="flex gap-3 pt-4">
                  <Button
                    type="submit"
                    disabled={loading}
                    className="flex-1"
                  >
                    {loading ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Processing Transcript...
                      </>
                    ) : (
                      <>
                        <Upload className="mr-2 h-4 w-4" />
                        Generate Insights
                      </>
                    )}
                  </Button>
                  
                  {onCancel && (
                    <Button
                      type="button"
                      variant="outline"
                      onClick={onCancel}
                      disabled={loading}
                    >
                      Cancel
                    </Button>
                  )}
                </div>
              </form>
            </TabsContent>

            <TabsContent value="file" className="mt-6">
              <form onSubmit={handleFileSubmit} className="space-y-6">
                {error && (
                  <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-md text-red-700">
                    <AlertCircle className="h-4 w-4" />
                    <span className="text-sm">{error}</span>
                  </div>
                )}

                <div className="space-y-2">
                  <Label htmlFor="transcript_file">Transcript File</Label>
                  <Input
                    id="transcript_file"
                    type="file"
                    accept=".pdf,.docx,.doc,.txt,.rtf,.odt"
                    onChange={handleFileChange}
                    disabled={loading}
                    className="w-full"
                  />
                  <p className="text-xs text-gray-500">
                    Supported formats: PDF, DOCX, DOC, TXT, RTF, ODT (max 10MB)
                  </p>
                </div>

                <div className="flex gap-3 pt-4">
                  <Button
                    type="submit"
                    disabled={loading}
                    className="flex-1"
                  >
                    {loading ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Processing File...
                      </>
                    ) : (
                      <>
                        <Upload className="mr-2 h-4 w-4" />
                        Generate Insights
                      </>
                    )}
                  </Button>
                  
                  {onCancel && (
                    <Button
                      type="button"
                      variant="outline"
                      onClick={onCancel}
                      disabled={loading}
                    >
                      Cancel
                    </Button>
                  )}
                </div>
              </form>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
}