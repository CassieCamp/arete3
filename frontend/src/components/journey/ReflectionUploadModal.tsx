import React, { useState } from 'react';
import { LEADERSHIP_CATEGORIES } from '../../config/leadershipCategories';

// --- Placeholder Implementations ---
const getAuthToken = () => 'DUMMY_TOKEN';

const Modal: React.FC<{ isOpen: boolean; onClose: () => void; size?: string; children: React.ReactNode }> = ({ isOpen, onClose, children }) => 
  isOpen ? <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center" onClick={onClose}>
    <div className="bg-white rounded-lg shadow-xl w-full max-w-lg" onClick={e => e.stopPropagation()}>{children}</div>
  </div> : null;

const ModalHeader: React.FC<{ children: React.ReactNode }> = ({ children }) => <div className="p-6 border-b">{children}</div>;
const ModalTitle: React.FC<{ children: React.ReactNode }> = ({ children }) => <h2 className="text-xl font-semibold">{children}</h2>;
const ModalSubtitle: React.FC<{ children: React.ReactNode }> = ({ children }) => <p className="text-sm text-muted-foreground mt-1">{children}</p>;
const ModalContent: React.FC<{ children: React.ReactNode }> = ({ children }) => <div className="p-6">{children}</div>;
const ModalFooter: React.FC<{ children: React.ReactNode }> = ({ children }) => <div className="p-6 border-t flex justify-end gap-2">{children}</div>;

const Button: React.FC<React.ButtonHTMLAttributes<HTMLButtonElement> & { variant?: 'outline' }> = ({ className, variant, ...props }) => (
  <button className={`px-4 py-2 rounded-md font-semibold ${variant === 'outline' ? 'border border-border' : 'bg-primary text-primary-foreground'} ${className}`} {...props} />
);

const FileDropZone: React.FC<{ onFileSelect: (file: File | null) => void; selectedFile: File | null; acceptedTypes: string[]; maxSize: number; }> = ({ onFileSelect, selectedFile }) => (
  <div className="border-2 border-dashed border-border rounded-lg p-8 text-center">
    <input type="file" className="hidden" onChange={e => onFileSelect(e.target.files ? e.target.files[0] : null)} />
    <p>{selectedFile ? selectedFile.name : 'Drag & drop or click to select a file'}</p>
    <button onClick={() => document.querySelector<HTMLInputElement>('input[type="file"]')?.click()} className="text-primary mt-2">Browse</button>
  </div>
);

const UploadProgress = () => <div className="text-center p-8">Uploading...</div>;
const ProcessingStatus = () => <div className="text-center p-8">Processing...</div>;
// --- End Placeholder Implementations ---

interface ReflectionUploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

const ReflectionUploadModal = ({ isOpen, onClose, onSuccess }: ReflectionUploadModalProps) => {
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [uploading, setUploading] = useState(false);
  const [processing, setProcessing] = useState(false);

  const handleUpload = async () => {
    if (!file) return;

    try {
      setUploading(true);
      
      const formData = new FormData();
      formData.append('file', file);
      formData.append('title', title);
      formData.append('description', description);

      const response = await fetch('/api/v1/reflections/upload', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${getAuthToken()}` },
        body: formData
      });

      if (!response.ok) {
        throw new Error('Upload failed');
      }

      const result = await response.json();
      
      setUploading(false);
      setProcessing(true);
      
      await pollForProcessing(result.reflection.id);
      
      onSuccess();
      onClose();
    } catch (error) {
      setUploading(false);
      setProcessing(false);
      // Handle error
    }
  };

  const pollForProcessing = async (reflectionId: string) => {
    const maxAttempts = 30; // 30 seconds max
    let attempts = 0;
    
    while (attempts < maxAttempts) {
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      try {
        const response = await fetch(`/api/v1/reflections/${reflectionId}`, {
          headers: { 'Authorization': `Bearer ${getAuthToken()}` }
        });
        
        const reflection = await response.json();
        
        if (reflection.status === 'processed') {
          setProcessing(false);
          return;
        }
        
        if (reflection.status === 'failed') {
          throw new Error('Processing failed');
        }
      } catch (error) {
        console.error('Polling error:', error);
      }
      
      attempts++;
    }
    
    setProcessing(false);
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="lg">
      <ModalHeader>
        <ModalTitle>Add Leadership Reflection</ModalTitle>
        <ModalSubtitle>
          Upload a document to generate AI insights across the 4 leadership development areas
        </ModalSubtitle>
      </ModalHeader>
      
      <ModalContent>
        {!uploading && !processing ? (
          <div className="space-y-6">
            <FileDropZone
              onFileSelect={setFile}
              selectedFile={file}
              acceptedTypes={['.pdf', '.docx', '.txt']}
              maxSize={10 * 1024 * 1024} // 10MB
            />
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Title (optional)
              </label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="AI will generate a title if left blank"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Description (optional)
              </label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Add context about this reflection..."
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            
            <div className="bg-muted/30 p-4 rounded-lg border border-border">
              <h4 className="text-sm font-medium text-foreground mb-3">
                AI will analyze for insights in these leadership areas:
              </h4>
              <div className="grid grid-cols-2 gap-2">
                {LEADERSHIP_CATEGORIES.map(category => (
                  <div key={category.key} className="flex items-center gap-2 text-sm">
                    <span>{category.icon}</span>
                    <span className="text-muted-foreground">{category.shortLabel}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : uploading ? (
          <UploadProgress />
        ) : (
          <ProcessingStatus />
        )}
      </ModalContent>
      
      <ModalFooter>
        {!uploading && !processing ? (
          <>
            <Button variant="outline" onClick={onClose}>Cancel</Button>
            <Button 
              onClick={handleUpload}
              disabled={!file}
              className="bg-blue-600 hover:bg-blue-700"
            >
              Upload & Analyze
            </Button>
          </>
        ) : (
          <Button variant="outline" onClick={onClose}>Close</Button>
        )}
      </ModalFooter>
    </Modal>
  );
};

export default ReflectionUploadModal;