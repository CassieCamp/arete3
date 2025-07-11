# Sprint S10.3: Unified Entry System

**Epic**: [Sprint S10 Application Redesign](./sprint_s10_redesign_epic.md)  
**Duration**: 2 weeks  
**Priority**: High  
**Dependencies**: Sprint S10.1 (Foundation), Sprint S10.2 (Landing Page)

## Sprint Overview

This sprint implements the unified entry system that allows users to create both session transcripts and fresh thoughts through a single interface. It includes AI-powered title generation, goal detection, and freemium gating to limit non-coached users to 3 entries.

## Sprint Goals

1. **Implement unified entry creation modal** with tab switching between entry types
2. **Build session and fresh thought forms** with file upload and text input
3. **Add AI title generation** and goal detection pipeline
4. **Implement freemium gating** with entry limits and upgrade prompts
5. **Create entry processing pipeline** with enhanced AI insights

## Wireframe Reference

Based on wireframe analysis:
- **Single entry CTA** that opens modal with type selection
- **Tab interface** for "Recent Session" vs "Fresh Thoughts"
- **File upload** for session transcripts (.txt files)
- **Text input** for both types with date selection
- **AI-generated titles** displayed after processing
- **Goal suggestions** from AI analysis

## Frontend Components

### 1. Unified Entry Modal
```typescript
// File: frontend/src/components/entries/UnifiedEntryModal.tsx

interface UnifiedEntryModalProps {
  isOpen: boolean;
  onClose: () => void;
  freemiumStatus: FreemiumStatus;
}

export function UnifiedEntryModal({ isOpen, onClose, freemiumStatus }: UnifiedEntryModalProps) {
  const [activeTab, setActiveTab] = useState<'session' | 'fresh_thought'>('session');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showGoalSuggestions, setShowGoalSuggestions] = useState(false);
  const [detectedGoals, setDetectedGoals] = useState<DetectedGoal[]>([]);
  const [createdEntryId, setCreatedEntryId] = useState<string>('');
  
  const canCreateEntry = freemiumStatus.has_coach || freemiumStatus.entries_remaining > 0;
  
  if (!isOpen) return null;
  
  const handleEntrySubmit = async (entryData: EntryFormData) => {
    setIsSubmitting(true);
    try {
      const response = await fetch('/api/v1/entries', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...entryData,
          entry_type: activeTab
        })
      });
      
      if (response.ok) {
        const result = await response.json();
        setCreatedEntryId(result.id);
        
        // Show goal suggestions if detected
        if (result.detected_goals?.length > 0) {
          setDetectedGoals(result.detected_goals);
          setShowGoalSuggestions(true);
        } else {
          onClose();
          // Show success message
          showSuccessToast(`${activeTab === 'session' ? 'Session' : 'Thought'} added successfully!`);
        }
      } else {
        const error = await response.json();
        throw new Error(error.message || 'Failed to create entry');
      }
    } catch (error) {
      console.error('Error creating entry:', error);
      showErrorToast(error.message || 'Failed to create entry. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };
  
  const handleGoalSuggestionsComplete = () => {
    setShowGoalSuggestions(false);
    onClose();
    showSuccessToast('Entry and destinations added successfully!');
  };
  
  return (
    <>
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div className="bg-white rounded-xl max-w-2xl w-full max-h-[90vh] overflow-hidden">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b">
            <h2 className="text-xl font-semibold">Add Entry</h2>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
          
          {/* Freemium Gate Check */}
          {!canCreateEntry ? (
            <FreemiumEntryGate 
              freemiumStatus={freemiumStatus}
              onClose={onClose}
            />
          ) : (
            <>
              {/* Tab Navigation */}
              <div className="flex border-b">
                <button
                  onClick={() => setActiveTab('session')}
                  className={`flex-1 py-4 px-6 text-center font-medium transition-colors ${
                    activeTab === 'session'
                      ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50'
                      : 'text-gray-600 hover:text-gray-800'
                  }`}
                >
                  <div className="flex items-center justify-center space-x-2">
                    <FileText className="w-4 h-4" />
                    <span>Recent Session</span>
                  </div>
                </button>
                <button
                  onClick={() => setActiveTab('fresh_thought')}
                  className={`flex-1 py-4 px-6 text-center font-medium transition-colors ${
                    activeTab === 'fresh_thought'
                      ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50'
                      : 'text-gray-600 hover:text-gray-800'
                  }`}
                >
                  <div className="flex items-center justify-center space-x-2">
                    <MessageSquare className="w-4 h-4" />
                    <span>Fresh Thoughts</span>
                  </div>
                </button>
              </div>
              
              {/* Tab Content */}
              <div className="p-6 overflow-y-auto max-h-[60vh]">
                {activeTab === 'session' ? (
                  <SessionEntryForm 
                    onSubmit={handleEntrySubmit}
                    isSubmitting={isSubmitting}
                    freemiumStatus={freemiumStatus}
                  />
                ) : (
                  <FreshThoughtEntryForm 
                    onSubmit={handleEntrySubmit}
                    isSubmitting={isSubmitting}
                    freemiumStatus={freemiumStatus}
                  />
                )}
              </div>
            </>
          )}
        </div>
      </div>
      
      {/* Goal Suggestions Modal */}
      <GoalSuggestionsModal
        isOpen={showGoalSuggestions}
        onClose={handleGoalSuggestionsComplete}
        entryId={createdEntryId}
        detectedGoals={detectedGoals}
      />
    </>
  );
}
```

### 2. Session Entry Form
```typescript
// File: frontend/src/components/entries/SessionEntryForm.tsx

interface SessionEntryFormProps {
  onSubmit: (data: EntryFormData) => Promise<void>;
  isSubmitting: boolean;
  freemiumStatus: FreemiumStatus;
}

export function SessionEntryForm({ onSubmit, isSubmitting, freemiumStatus }: SessionEntryFormProps) {
  const [formData, setFormData] = useState({
    content: '',
    session_date: new Date().toISOString().split('T')[0],
    input_method: 'paste' as 'paste' | 'upload',
    file_name: '',
    title: ''
  });
  const [dragActive, setDragActive] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  
  const handleFileUpload = async (file: File) => {
    if (file.type !== 'text/plain') {
      setErrors({ file: 'Please upload a .txt file' });
      return;
    }
    
    if (file.size > 5 * 1024 * 1024) { // 5MB limit
      setErrors({ file: 'File size must be less than 5MB' });
      return;
    }
    
    try {
      const content = await file.text();
      setFormData(prev => ({
        ...prev,
        content,
        input_method: 'upload',
        file_name: file.name
      }));
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
                  Drop your .txt file here or{' '}
                  <label className="text-blue-600 hover:text-blue-800 cursor-pointer">
                    browse
                    <input
                      type="file"
                      accept=".txt"
                      onChange={(e) => e.target.files?.[0] && handleFileUpload(e.target.files[0])}
                      className="hidden"
                    />
                  </label>
                </div>
                <div className="text-sm text-gray-600 mt-1">
                  Only .txt files are supported (max 5MB)
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
        <button
          type="submit"
          disabled={!formData.content.trim() || isSubmitting}
          className="flex-1 bg-blue-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
        >
          {isSubmitting ? (
            <div className="flex items-center justify-center space-x-2">
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              <span>Processing...</span>
            </div>
          ) : (
            'Add Session'
          )}
        </button>
      </div>
    </form>
  );
}
```

### 3. Fresh Thought Entry Form
```typescript
// File: frontend/src/components/entries/FreshThoughtEntryForm.tsx

interface FreshThoughtEntryFormProps {
  onSubmit: (data: EntryFormData) => Promise<void>;
  isSubmitting: boolean;
  freemiumStatus: FreemiumStatus;
}

export function FreshThoughtEntryForm({ onSubmit, isSubmitting, freemiumStatus }: FreshThoughtEntryFormProps) {
  const [formData, setFormData] = useState({
    content: '',
    session_date: new Date().toISOString().split('T')[0],
    input_method: 'paste' as const,
    title: ''
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [wordCount, setWordCount] = useState(0);
  
  useEffect(() => {
    const words = formData.content.trim().split(/\s+/).filter(word => word.length > 0);
    setWordCount(words.length);
  }, [formData.content]);
  
  const validateForm = () => {
    const newErrors: Record<string, string> = {};
    
    if (!formData.content.trim()) {
      newErrors.content = 'Please share your thoughts';
    } else if (formData.content.trim().length < 10) {
      newErrors.content = 'Please write at least 10 characters';
    }
    
    if (!formData.session_date) {
      newErrors.session_date = 'Date is required';
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
      {/* Content Input */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          What's on your mind? *
        </label>
        <textarea
          value={formData.content}
          onChange={(e) => setFormData(prev => ({ ...prev, content: e.target.value }))}
          placeholder="Share your thoughts, insights, reflections, or anything that's on your mind..."
          className={`w-full h-40 p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none ${
            errors.content ? 'border-red-500' : 'border-gray-300'
          }`}
          required
        />
        <div className="flex justify-between items-center mt-1">
          <div className="text-xs text-gray-500">
            {formData.content.length} characters • {wordCount} words
          </div>
          {errors.content && (
            <div className="text-xs text-red-500">{errors.content}</div>
          )}
        </div>
      </div>
      
      {/* Date */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Date *
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
        <button
          type="submit"
          disabled={!formData.content.trim() || isSubmitting}
          className="flex-1 bg-blue-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
        >
          {isSubmitting ? (
            <div className="flex items-center justify-center space-x-2">
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              <span>Processing...</span>
            </div>
          ) : (
            'Add Thought'
          )}
        </button>
      </div>
    </form>
  );
}
```

### 4. Freemium Entry Gate
```typescript
// File: frontend/src/components/freemium/FreemiumEntryGate.tsx

interface FreemiumEntryGateProps {
  freemiumStatus: FreemiumStatus;
  onClose: () => void;
}

export function FreemiumEntryGate({ freemiumStatus, onClose }: FreemiumEntryGateProps) {
  const [isRequestingCoach, setIsRequestingCoach] = useState(false);
  const [requestForm, setRequestForm] = useState({
    message: '',
    preferred_contact: 'email' as 'email' | 'phone',
    contact_info: ''
  });
  
  const handleRequestCoach = async () => {
    setIsRequestingCoach(true);
    try {
      await fetch('/api/v1/coach-request', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: requestForm.message || 'I would like to connect with a coach to unlock unlimited entries.',
          preferred_contact: requestForm.preferred_contact,
          contact_info: requestForm.contact_info
        })
      });
      
      showSuccessToast('Coach request submitted! We\'ll be in touch soon.');
      onClose();
    } catch (error) {
      console.error('Error requesting coach:', error);
      showErrorToast('Failed to submit coach request. Please try again.');
    } finally {
      setIsRequestingCoach(false);
    }
  };
  
  return (
    <div className="p-8">
      <div className="text-center mb-6">
        <div className="w-16 h-16 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <Lock className="w-8 h-8 text-orange-500" />
        </div>
        
        <h3 className="text-xl font-semibold text-gray-800 mb-2">
          Entry Limit Reached
        </h3>
        
        <p className="text-gray-600">
          You've used all {freemiumStatus.max_free_entries} of your free entries. 
          Connect with a coach to unlock unlimited entries and advanced features.
        </p>
      </div>
      
      <div className="space-y-6">
        <div className="bg-blue-50 rounded-lg p-4">
          <h4 className="font-medium text-blue-800 mb-3">With a coach, you get:</h4>
          <ul className="text-sm text-blue-700 space-y-2">
            <li className="flex items-center space-x-2">
              <Check className="w-4 h-4 text-blue-600" />
              <span>Unlimited entry creation</span>
            </li>
            <li className="flex items-center space-x-2">
              <Check className="w-4 h-4 text-blue-600" />
              <span>Advanced AI insights and analysis</span>
            </li>
            <li className="flex items-center space-x-2">
              <Check className="w-4 h-4 text-blue-600" />
              <span>Personalized coaching resources</span>
            </li>
            <li className="flex items-center space-x-2">
              <Check className="w-4 h-4 text-blue-600" />
              <span>Goal tracking and progress monitoring</span>
            </li>
            <li className="flex items-center space-x-2">
              <Check className="w-4 h-4 text-blue-600" />
              <span>Direct coach communication</span>
            </li>
          </ul>
        </div>
        
        {/* Coach Request Form */}
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Tell us about your coaching needs (optional)
            </label>
            <textarea
              value={requestForm.message}
              onChange={(e) => setRequestForm(prev => ({ ...prev, message: e.target.value }))}
              placeholder="What are you hoping to achieve with coaching?"
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              rows={3}
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Preferred contact method
            </label>
            <select
              value={requestForm.preferred_contact}
              onChange={(e) => setRequestForm(prev => ({ 
                ...prev, 
                preferred_contact: e.target.value as 'email' | 'phone' 
              }))}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="email">Email</option>
              <option value="phone">Phone</option>
            </select>
          </div>
        </div>
        
        <div className="flex space-x-3">
          <button
            onClick={onClose}
            className="flex-1 bg-gray-200 text-gray-800 py-3 px-4 rounded-lg font-medium hover:bg-gray-300 transition-colors"
          >
            Maybe Later
          </button>
          <button
            onClick={handleRequestCoach}
            disabled={isRequestingCoach}
            className="flex-1 bg-blue-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-300 transition-colors"
          >
            {isRequestingCoach ? 'Requesting...' : 'Request Coach'}
          </button>
        </div>
      </div>
    </div>
  );
}
```

### 5. Goal Suggestions Modal
```typescript
// File: frontend/src/components/entries/GoalSuggestionsModal.tsx

interface DetectedGoal {
  goal_statement: string;
  confidence: number;
}

interface GoalSuggestionsModalProps {
  isOpen: boolean;
  onClose: () => void;
  entryId: string;
  detectedGoals: DetectedGoal[];
}

export function GoalSuggestionsModal({ isOpen, onClose, entryId, detectedGoals }: GoalSuggestionsModalProps) {