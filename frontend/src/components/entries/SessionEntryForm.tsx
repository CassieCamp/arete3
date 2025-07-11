"use client";

import { useState, useEffect } from 'react';
import { Type, Upload, FileText, AlertTriangle } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface FreemiumStatus {
  has_coach: boolean;
  entries_count: number;
  max_free_entries: number;
  entries_remaining: number;
  can_create_entries: boolean;
  can_access_insights: boolean;
  is_freemium: boolean;
}

interface EntryFormData {
  content: string;
  session_date: string;
  input_method: 'paste' | 'upload';
  file_name?: string;
  title?: string;
  file?: File;
}

interface SessionEntryFormProps {
  onSubmit: (data: EntryFormData) => Promise<void>;
  isSubmitting: boolean;
  freemiumStatus: FreemiumStatus;
}

export function SessionEntryForm({ onSubmit, isSubmitting, freemiumStatus }: SessionEntryFormProps) {
  const [formData, setFormData] = useState<EntryFormData>({
    content: '',
    session_date: new Date().toISOString().split('T')[0],
    input_method: 'paste',
    file_name: '',
    title: ''
  });
  const [dragActive, setDragActive] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleFileUpload = async (file: File) => {
    if (file.type !== 'text/plain' && file.type !== 'application/pdf') {
      setErrors({ file: 'Please upload a .txt or .pdf file' });
      return;
    }
    
    if (file.size > 5 * 1024 * 1024) { // 5MB limit
      setErrors({ file: 'File size must be less than 5MB' });
      return;
    }
    
    try {
      if (file.type === 'text/plain') {
        // For text files, read content directly
        const content = await file.text();
        setFormData(prev => ({
          ...prev,
          content,
          input_method: 'upload',
          file_name: file.name,
          file: undefined // Clear file object for text files
        }));
      } else if (file.type === 'application/pdf') {
        // For PDF files, store the file object and show placeholder content
        setFormData(prev => ({
          ...prev,
          content: '[PDF file selected - content will be extracted during processing]',
          input_method: 'upload',
          file_name: file.name,
          file: file // Store the actual file object for PDF files
        }));
      }
      setErrors({});
    } catch (error) {
      console.error('Error reading file:', error);
      setErrors({ file: 'Error reading file. Please try again.' });
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
    
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFileUpload(files[0]);
    }
  };

  const validateForm = () => {
    const newErrors: Record<string, string> = {};
    
    if (!formData.content.trim()) {
      newErrors.content = 'Session content is required';
    }
    
    if (!formData.session_date) {
      newErrors.session_date = 'Session date is required';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) return;
    
    await onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Input Method Toggle */}
      <div className="flex space-x-4">
        <button
          type="button"
          onClick={() => setFormData(prev => ({ 
            ...prev, 
            input_method: 'paste', 
            content: '', 
            file_name: '' 
          }))}
          className={`flex-1 p-3 rounded-lg border-2 transition-colors ${
            formData.input_method === 'paste'
              ? 'border-blue-500 bg-blue-50 text-blue-700'
              : 'border-gray-300 hover:border-gray-400'
          }`}
        >
          <Type className="w-5 h-5 mx-auto mb-1" />
          <div className="text-sm font-medium">Paste Text</div>
        </button>
        <button
          type="button"
          onClick={() => setFormData(prev => ({ 
            ...prev, 
            input_method: 'upload', 
            content: '', 
            file_name: '' 
          }))}
          className={`flex-1 p-3 rounded-lg border-2 transition-colors ${
            formData.input_method === 'upload'
              ? 'border-blue-500 bg-blue-50 text-blue-700'
              : 'border-gray-300 hover:border-gray-400'
          }`}
        >
          <Upload className="w-5 h-5 mx-auto mb-1" />
          <div className="text-sm font-medium">Upload File</div>
        </button>
      </div>
      
      {/* Content Input */}
      {formData.input_method === 'paste' ? (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Session Content *
          </label>
          <textarea
            value={formData.content}
            onChange={(e) => setFormData(prev => ({ ...prev, content: e.target.value }))}
            placeholder="Paste your session transcript here..."
            className={`w-full h-40 p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none ${
              errors.content ? 'border-red-500' : 'border-gray-300'
            }`}
            required
          />
          <div className="flex justify-between items-center mt-1">
            <div className="text-xs text-gray-500">
              {formData.content.length} characters
            </div>
            {errors.content && (
              <div className="text-xs text-red-500">{errors.content}</div>
            )}
          </div>
        </div>
      ) : (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Upload Session File *
          </label>
          <div
            onDrop={handleDrop}
            onDragOver={(e) => { e.preventDefault(); setDragActive(true); }}
            onDragLeave={() => setDragActive(false)}
            className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
              dragActive
                ? 'border-blue-500 bg-blue-50'
                : errors.file
                ? 'border-red-500 bg-red-50'
                : 'border-gray-300 hover:border-gray-400'
            }`}
          >
            {formData.file_name ? (
              <div>
                <FileText className="w-8 h-8 mx-auto mb-2 text-green-500" />
                <div className="font-medium text-gray-800">{formData.file_name}</div>
                <div className="text-sm text-gray-600 mt-1">
                  {formData.content.length} characters loaded
                </div>
                <button
                  type="button"
                  onClick={() => setFormData(prev => ({ ...prev, content: '', file_name: '' }))}
                  className="mt-2 text-sm text-blue-600 hover:text-blue-800"
                >
                  Remove file
                </button>
              </div>
            ) : (
              <div>
                <Upload className="w-8 h-8 mx-auto mb-2 text-gray-400" />
                <div className="font-medium text-gray-800">
                  Drop your .txt or .pdf file here or{' '}
                  <label className="text-blue-600 hover:text-blue-800 cursor-pointer">
                    browse
                    <input
                      type="file"
                      accept=".txt,.pdf"
                      onChange={(e) => e.target.files?.[0] && handleFileUpload(e.target.files[0])}
                      className="hidden"
                    />
                  </label>
                </div>
                <div className="text-sm text-gray-600 mt-1">
                  Only .txt and .pdf files are supported (max 5MB)
                </div>
              </div>
            )}
          </div>
          {errors.file && (
            <div className="mt-1 text-xs text-red-500">{errors.file}</div>
          )}
        </div>
      )}
      
      {/* Session Date */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Session Date *
        </label>
        <input
          type="date"
          value={formData.session_date}
          onChange={(e) => setFormData(prev => ({ ...prev, session_date: e.target.value }))}
          max={new Date().toISOString().split('T')[0]}
          className={`w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
            errors.session_date ? 'border-red-500' : 'border-gray-300'
          }`}
          required
        />
        {errors.session_date && (
          <div className="mt-1 text-xs text-red-500">{errors.session_date}</div>
        )}
      </div>
      
      {/* Optional Title */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Title (Optional)
        </label>
        <input
          type="text"
          value={formData.title}
          onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
          placeholder="AI will generate a title if left blank"
          maxLength={100}
          className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
        <div className="mt-1 text-xs text-gray-500">
          {formData.title ? `${formData.title.length}/100 characters` : 'Leave blank for AI-generated title'}
        </div>
      </div>
      
      {/* Freemium Warning */}
      {!freemiumStatus.has_coach && (
        <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
          <div className="flex items-start space-x-3">
            <AlertTriangle className="w-5 h-5 text-orange-500 mt-0.5 flex-shrink-0" />
            <div>
              <div className="font-medium text-orange-800">
                {freemiumStatus.entries_remaining} free entries remaining
              </div>
              <div className="text-sm text-orange-700 mt-1">
                Connect with a coach for unlimited entries and advanced features.
              </div>
            </div>
          </div>
        </div>
      )}
      
      {/* Submit Button */}
      <div className="flex space-x-3">
        <Button
          type="submit"
          disabled={!formData.content.trim() || isSubmitting}
          className="flex-1"
        >
          {isSubmitting ? (
            <div className="flex items-center justify-center space-x-2">
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              <span>Processing...</span>
            </div>
          ) : (
            'Add Session'
          )}
        </Button>
      </div>
    </form>
  );
}