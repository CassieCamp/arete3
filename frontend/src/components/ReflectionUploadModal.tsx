import React, { useState } from 'react';
import { X, Upload, Loader2 } from 'lucide-react';

interface ReflectionUploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onUpload: (file: File) => Promise<boolean>;
  uploading: boolean;
}

export const ReflectionUploadModal: React.FC<ReflectionUploadModalProps> = ({
  isOpen,
  onClose,
  onUpload,
  uploading
}) => {
  const [dragActive, setDragActive] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'success' | 'error'>('idle');

  if (!isOpen) return null;

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
    
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      await handleUpload(files[0]);
    }
  };

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      await handleUpload(files[0]);
    }
  };

  const handleUpload = async (file: File) => {
    const success = await onUpload(file);
    setUploadStatus(success ? 'success' : 'error');
    
    if (success) {
      setTimeout(() => {
        onClose();
        setUploadStatus('idle');
      }, 1500);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-background/95 backdrop-blur-md border border-border rounded-lg max-w-md w-full p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-medium text-foreground">Add Reflection</h2>
          <button
            onClick={onClose}
            className="text-muted-foreground hover:text-foreground"
            disabled={uploading}
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div
          className={`
            relative border-2 border-dashed rounded-lg p-8 text-center transition-colors
            ${dragActive ? 'border-primary bg-primary/5' : 'border-border'}
            ${uploading ? 'opacity-50 pointer-events-none' : 'cursor-pointer hover:border-primary/50'}
          `}
          onDrop={handleDrop}
          onDragOver={(e) => { e.preventDefault(); setDragActive(true); }}
          onDragLeave={() => setDragActive(false)}
        >
          <input
            type="file"
            accept=".pdf,.txt,.docx"
            onChange={handleFileSelect}
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            disabled={uploading}
          />

          {uploading ? (
            <div className="flex flex-col items-center gap-3">
              <Loader2 className="w-8 h-8 text-primary animate-spin" />
              <p className="text-sm text-muted-foreground">Processing your reflection...</p>
            </div>
          ) : uploadStatus === 'success' ? (
            <div className="flex flex-col items-center gap-3">
              <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                <span className="text-white text-sm">✓</span>
              </div>
              <p className="text-sm text-foreground">Upload successful!</p>
            </div>
          ) : (
            <div className="flex flex-col items-center gap-3">
              <Upload className="w-8 h-8 text-muted-foreground" />
              <div>
                <p className="text-sm font-medium text-foreground mb-1">
                  Drop your document here or click to browse
                </p>
                <p className="text-xs text-muted-foreground">
                  Supports PDF, TXT, and DOCX files
                </p>
              </div>
            </div>
          )}
        </div>

        {uploadStatus === 'error' && (
          <p className="text-sm text-red-500 text-center mt-4">
            Upload failed. Please try again.
          </p>
        )}
      </div>
    </div>
  );
};